import pandas as pd
import numpy as np
import config

file_blackpool = next(config.DATA_DIR.rglob('domestic-E06000009-*.csv'))
df_blackpool = pd.read_csv(file_blackpool)
file_cityoflondon = next(config.DATA_DIR.rglob('domestic-E09000001-*.csv'))
df_cityoflondon = pd.read_csv(file_cityoflondon)
file_westminster = next(config.DATA_DIR.rglob('domestic-E09000033-*.csv'))
df_westminster = pd.read_csv(file_westminster)

##print('Blackpool')
##print("Rows: ", df_blackpool.shape[0], "Columns: ", df_blackpool.shape[1])
##print(df_blackpool.dtypes.to_string())
##print(df_blackpool.iloc[0])
##print('City of London')
##print("Rows: ", df_cityoflondon.shape[0], "Columns: ", df_cityoflondon.shape[1])
##print(df_cityoflondon.dtypes.to_string())
##print(df_cityoflondon.iloc[0])
##print('Westminster')
##print("Rows: ", df_westminster.shape[0], "Columns: ", df_westminster.shape[1])
##print(df_westminster.dtypes.to_string())
##print(df_westminster.iloc[0])

common_cols = list(set(df_blackpool.columns) & set(df_cityoflondon.columns) & set(df_westminster.columns))
##print(f"Columns in all three datasets: {len(common_cols)}")
##for col in sorted(common_cols):
    ##print(f"  {col}")



##print("Blackpool null")
##print(df_blackpool[common_cols].isnull().mean().mul(100).to_string())
##print("City of London null")
##print(df_cityoflondon[common_cols].isnull().mean().mul(100).to_string())
##print("Westminster null")
##print(df_westminster[common_cols].isnull().mean().mul(100).to_string())

# Numeric feature analysis for common columns

numeric_cols = [
    'TOTAL_FLOOR_AREA',
    'CURRENT_ENERGY_EFFICIENCY',
    'CO2_EMISSIONS_CURRENT',
    'CO2_EMISS_CURR_PER_FLOOR_AREA',
    'ENERGY_CONSUMPTION_CURRENT',
    'ENVIRONMENT_IMPACT_CURRENT'
]

##print('Blackpool')
##print(df_blackpool[numeric_cols].describe().T.round(2).to_string())
##print('City of London')
##print(df_cityoflondon[numeric_cols].describe().T.round(2).to_string())
##print("Westminster")
##print(df_westminster[numeric_cols].describe().T.round(2).to_string())

# Categorical feature analysis for common columns

cat_cols = [
    'PROPERTY_TYPE',
    'BUILT_FORM',
    'MAIN_FUEL',
    'CURRENT_ENERGY_RATING',
    'MAINHEAT_DESCRIPTION'
]

##print("Blackpool")
##print(df_blackpool[cat_cols].describe().T.to_string())
##print("Westminster")
##print(df_westminster[cat_cols].describe().T.to_string())
##print("City of London")
##print(df_cityoflondon[cat_cols].describe().T.to_string())

# Duplicate Values

dfs = [('Blackpool', df_blackpool), ('Westminster', df_westminster), ('City of London', df_cityoflondon)]

for name, df in dfs:
    total_rows = len(df)
    unique_props = df['BUILDING_REFERENCE_NUMBER'].nunique()
    duplicate_rows = total_rows - unique_props
    dupe_rate = (duplicate_rows / total_rows) * 100
    max_inspections = df['BUILDING_REFERENCE_NUMBER'].value_counts().max()

    ##print(f"{name}")
    ##print(f"Total rows: {total_rows}")
    ##print(f"Unique properties: {unique_props}")
    ##print(f"Duplicate rows: {duplicate_rows}")
    ##print(f"Duplication rate: {dupe_rate:.1f}%")
    ##print(f"Max inspections: {max_inspections}")

# Correlation Check

pairs = [
    ('CURRENT_ENERGY_EFFICIENCY', 'ENVIRONMENT_IMPACT_CURRENT'),
    ('CO2_EMISSIONS_CURRENT', 'ENERGY_CONSUMPTION_CURRENT'),
    ('CO2_EMISSIONS_CURRENT', 'CO2_EMISS_CURR_PER_FLOOR_AREA'),
    ('TOTAL_FLOOR_AREA', 'CO2_EMISSIONS_CURRENT'),
    ('TOTAL_FLOOR_AREA', 'ENERGY_CONSUMPTION_CURRENT'),
]

for name, df in dfs:
    print(f"{name}")
    for col1, col2 in pairs:
        r = df[[col1, col2]].corr().iloc[0, 1]
        print(f"  {col1} vs {col2}: r={r:.2f}")
