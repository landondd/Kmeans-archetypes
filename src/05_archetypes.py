import pandas as pd
import matplotlib.pyplot as plt
import os
import config

df = pd.read_parquet(config.CLUSTERED_FILE)

# Remove clusters 6 and 11
df = df[(df['cluster'] != 6) & (df['cluster'] != 11)].copy()

numeric_cols = [
    'TOTAL_FLOOR_AREA',
    'CURRENT_ENERGY_EFFICIENCY',
    'CO2_EMISSIONS_CURRENT',
    'CO2_EMISS_CURR_PER_FLOOR_AREA',
    'CURRENT_ENERGY_RATING'
]

# Find average of numeric values for each cluster

profile = df.groupby('cluster')[numeric_cols].mean().round(1)

# Convert CURRENT_ENERGY_RATING back to ENERGY_RATING_LETTER
rating_map = {1: 'G', 2: 'F', 3: 'E', 4: 'D', 5: 'C', 6: 'B', 7: 'A'}
profile['ENERGY_RATING_LETTER'] = profile['CURRENT_ENERGY_RATING'].round(0).astype(int).map(rating_map)

property_cols = [c for c in df.columns if c.startswith('PROPERTY_TYPE_')]
built_cols = [c for c in df.columns if c.startswith('BUILT_FORM_')]
fuel_cols = [c for c in df.columns if c.startswith('MAIN_FUEL_')]

def dominant_category(group, cols):
    means = group[cols].mean()
    dominant = means.idxmax()
    pct = means.max() * 100
    return f"{dominant.split('_', 2)[2]} ({pct:.1f}%)"

categorical_profile = df.groupby('cluster').apply(
    lambda g: pd.Series({
        'dominant_property_type': dominant_category(g, property_cols),
        'dominant_built_form': dominant_category(g, built_cols),
        'dominant_fuel_type': dominant_category(g, fuel_cols)
    })
)

# CO2 emission savings per cluster
co2_analysis = df.groupby('cluster').agg(
    cluster_size=('CO2_EMISSIONS_CURRENT', 'count'),
    avg_co2_emissions=('CO2_EMISSIONS_CURRENT', 'mean')).round(4)

self_consumed_kwh = 855
co2_factor = 0.136

co2_saved_per_home_kg = self_consumed_kwh * co2_factor
co2_saved_per_home_tonnes = co2_saved_per_home_kg / 1000

co2_analysis['co2_saved_per_home_kg'] = round(co2_saved_per_home_kg, 2)
co2_analysis['co2_saved_total_tonnes'] = (co2_analysis['cluster_size'] * co2_saved_per_home_tonnes).round(0).astype(int)
co2_analysis['pct_co2_reduction'] = ((co2_saved_per_home_tonnes / co2_analysis['avg_co2_emissions'])* 100).round(2)

co2_ranked = co2_analysis.sort_values('pct_co2_reduction', ascending=False)

# Table 1
table1 = profile.join(co2_analysis['cluster_size']).join(categorical_profile)
table1 = table1.rename(columns={'cluster_size': 'home_count'})
table1 = table1[['home_count',
                 'TOTAL_FLOOR_AREA', 'CURRENT_ENERGY_EFFICIENCY', 'ENERGY_RATING_LETTER',
                 'CO2_EMISSIONS_CURRENT', 'CO2_EMISS_CURR_PER_FLOOR_AREA',
                 'dominant_property_type', 'dominant_built_form', 'dominant_fuel_type']]
table1 = table1.reset_index()  
table1.to_csv(config.TABLES_DIR / 'table1_archetype_profile.csv', index=False)

# Table 2
table2 = co2_ranked.reset_index()  
table2.insert(0, 'rank', range(1, len(table2) + 1))
table2 = table2[['rank', 'cluster', 'cluster_size', 'avg_co2_emissions',
                 'co2_saved_per_home_kg', 'co2_saved_total_tonnes', 'pct_co2_reduction']]
table2.to_csv(config.TABLES_DIR / 'table2_savings_ranking.csv', index=False)
print(table2.to_string(index=False))

# Figure -  Absolute CO2 saved per cluster
abs_saved = co2_analysis['co2_saved_total_tonnes'].sort_values(ascending=False)
plt.figure(figsize=(12, 5))
plt.bar(abs_saved.index.astype(str), abs_saved.values, color='green')
plt.xlabel('Cluster (ranked by total CO₂ saved)')
plt.ylabel('Total CO₂ saved (tonnes/year)')
plt.title('Total CO₂ Saved per Cluster from Solar')
plt.tight_layout()
plt.savefig(config.FIGURES_DIR / 'co2_absolute_saved.png', dpi=150)
plt.close()