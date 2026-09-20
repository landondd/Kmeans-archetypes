import pandas as pd
import numpy as np
import os
import glob
from sklearn.preprocessing import StandardScaler
import joblib
import config

feature_cols = [
    'TOTAL_FLOOR_AREA',
    'CURRENT_ENERGY_EFFICIENCY',
    'CO2_EMISSIONS_CURRENT',
    'CO2_EMISS_CURR_PER_FLOOR_AREA',
    'PROPERTY_TYPE',
    'BUILT_FORM',
    'CURRENT_ENERGY_RATING',
    'MAIN_FUEL'
]

id_cols = [
    'BUILDING_REFERENCE_NUMBER',
    'LMK_KEY',
    'Latitude',
    'Longitude'
]

def load_and_clean(filepath):
    df = pd.read_csv(filepath, low_memory=False)
    df = df.drop(columns=['Unnamed: 0'])
    cols_to_keep = [c for c in feature_cols + id_cols if c in df.columns]
    df = df[cols_to_keep]
    stem = os.path.splitext(os.path.basename(filepath))[0]
    local_authority = stem.split('-', 2)[2].replace('-', ' ')
    df['LOCAL_AUTHORITY'] = local_authority
    return df

##test_df = load_and_clean(next(config.DATA_DIR.rglob('domestic-E07000148-*.csv')))
##print(test_df.shape)
##print(test_df.columns.tolist())

# Path to folder with all data for me to use
data_dir = str(config.DATA_DIR)

# This code sourced from: https://docs.python.org/3/library/glob.html
# Supplemental source 1: https://stackoverflow.com/questions/2186525/how-to-use-glob-to-find-files-recursively
all_files = glob.glob(os.path.join(data_dir, '**', '*.csv'), recursive=True)

dfs = []

for filepath in all_files:
    dfs.append(load_and_clean(filepath))


df_raw = pd.concat(dfs, ignore_index=True)
##print(f'Total rows: {df_raw.shape[0]}')
##print(f'Total columns: {df_raw.shape[1]}')

# Convert LMK_KEY to date format
df_raw['INSPECTION_DATE_PARSED'] = pd.to_datetime(df_raw['LMK_KEY'].str[8:16], format='%Y%m%d', errors='coerce')

# Sort the dataframe by the building reference number and the inspection date
df_raw = df_raw.sort_values(['BUILDING_REFERENCE_NUMBER', 'INSPECTION_DATE_PARSED'])

# Keep only most recent inspection
df_deduped = df_raw.drop_duplicates(subset='BUILDING_REFERENCE_NUMBER', keep='last')

# Drop the LMK_KEY and the inspection date we used to filter out duplicates
df_deduped = df_deduped.drop(columns=['LMK_KEY', 'INSPECTION_DATE_PARSED'])

# Print summary of results after deduplication

print(f'Rows before deduplication: {df_raw.shape[0]}')
print(f'Rows after deduplication: {df_deduped.shape[0]}')
print(f'Rows removed: {df_raw.shape[0] - df_deduped.shape[0]}')

# Remove invalid rows

##print(f'Rows before invalid value removal: {df_deduped.shape[0]}')
df_deduped = df_deduped[df_deduped['TOTAL_FLOOR_AREA'] > 0]
##print(f'After TOTAL_FLOOR_AREA filter: {df_deduped.shape[0]}')
df_deduped = df_deduped[df_deduped['CO2_EMISSIONS_CURRENT'] > 0]
##print(f'After CO2_EMISSIONS_CURRENT filter: {df_deduped.shape[0]}')
df_deduped = df_deduped[df_deduped['CO2_EMISS_CURR_PER_FLOOR_AREA'] >= 0]
##print(f'After CO2_EMISS_CURR_PER_FLOOR_AREA filter: {df_deduped.shape[0]}')
df_deduped = df_deduped[df_deduped['CURRENT_ENERGY_EFFICIENCY'] > 1]
##print(f'After CURRENT_ENERGY_EFFICIENCY filter: {df_deduped.shape[0]}')

# Consolidate MAIN_FUEL categories
def consolidate_fuel(value):
    if pd.isna(value):
        return 'other'
    v = value.lower()
    if 'gas' in v or 'lpg' in v:
        return 'gas'
    elif 'electric' in v:
        return 'electric'
    elif 'oil' in v:
        return 'oil'
    else:
        return 'other'

df_deduped['MAIN_FUEL'] = df_deduped['MAIN_FUEL'].apply(consolidate_fuel)
print(df_deduped['MAIN_FUEL'].value_counts())

# Remove the outliers
for col in ['TOTAL_FLOOR_AREA', 'CO2_EMISSIONS_CURRENT', 'CO2_EMISS_CURR_PER_FLOOR_AREA']:
    cap = df_deduped[col].quantile(0.99)
    rows_capped = (df_deduped[col] > cap).sum()
    ##print(f'{col}: cap={cap:.2f}, rows capped={rows_capped}')
    df_deduped[col] = df_deduped[col].clip(upper=cap)

# Encode CURRENT_ENERGY_RATING feature

ratings = {'G': 1, 'F': 2, 'E': 3, 'D': 4, 'C': 5, 'B': 6, 'A': 7}
df_deduped['CURRENT_ENERGY_RATING'] = df_deduped['CURRENT_ENERGY_RATING'].map(ratings)
##print(df_deduped['CURRENT_ENERGY_RATING'].isna().sum())

# If any energy ratings cannot be found after encoding I drop them

##print('Before drop: ', df_deduped.shape[0])
df_deduped = df_deduped.dropna(subset=['CURRENT_ENERGY_RATING'])
##print('After drop: ', df_deduped.shape[0])

# One-hot encode categorical features

df_deduped = pd.get_dummies(df_deduped, columns=['PROPERTY_TYPE', 'BUILT_FORM', 'MAIN_FUEL'], drop_first=False)
##print(df_deduped.columns.tolist())

# Scale Numeric Features
clustering_cols = [
    'TOTAL_FLOOR_AREA', 'CURRENT_ENERGY_EFFICIENCY', 'CO2_EMISSIONS_CURRENT',
    'CO2_EMISS_CURR_PER_FLOOR_AREA', 'CURRENT_ENERGY_RATING',
    'PROPERTY_TYPE_Bungalow', 'PROPERTY_TYPE_Flat', 'PROPERTY_TYPE_House',
    'PROPERTY_TYPE_Maisonette', 'BUILT_FORM_Detached', 'BUILT_FORM_Enclosed End-Terrace',
    'BUILT_FORM_Enclosed Mid-Terrace', 'BUILT_FORM_End-Terrace', 'BUILT_FORM_Mid-Terrace',
    'BUILT_FORM_NO DATA!', 'BUILT_FORM_Semi-Detached', 'MAIN_FUEL_electric',
    'MAIN_FUEL_gas', 'MAIN_FUEL_oil', 'MAIN_FUEL_other'
]

df_clean = df_deduped.copy()


# Scaler information sourced here: https://stackoverflow.com/questions/57911759/how-to-properly-use-a-scaler-model
df_scaled = df_deduped[clustering_cols].copy()
scaler = StandardScaler()
df_scaled[clustering_cols] = scaler.fit_transform(df_scaled[clustering_cols])

print(df_clean.shape)
print(df_scaled.shape)

# Save these files as .parquet files
# Parquet source code here: https://stackoverflow.com/questions/60930652/pandas-df-to-parquet-write-got-an-unexpected-keyword-argument-index-when-ign
df_scaled.to_parquet(config.SCALED_FILE, index=False)
df_clean.to_parquet(config.CLEAN_FILE, index=False)