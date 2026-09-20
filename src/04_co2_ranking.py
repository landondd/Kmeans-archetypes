import pandas as pd
import matplotlib.pyplot as plt
import config

df = pd.read_parquet(config.CLUSTERED_FILE)

# Remove clusters 6 and 11 (these were the clusters with low volume of buildings so were dropped)

df = df[(df['cluster'] != 6) & (df['cluster'] != 11)].copy()

# C02 emission savings per cluster
co2_analysis = df.groupby('cluster').agg(
    cluster_size=('CO2_EMISSIONS_CURRENT', 'count'),
    avg_co2_emissions=('CO2_EMISSIONS_CURRENT', 'mean'),
    avg_floor_area=('TOTAL_FLOOR_AREA', 'mean'),
    avg_energy_efficiency=('CURRENT_ENERGY_EFFICIENCY', 'mean')).round(4)

self_consumed_kwh = 855       
co2_factor = 0.136               

co2_saved_per_home_kg = self_consumed_kwh * co2_factor
co2_saved_per_home_tonnes = co2_saved_per_home_kg/1000
co2_analysis['pct_co2_reduction'] = ((co2_saved_per_home_tonnes / co2_analysis['avg_co2_emissions']) *100).round(2)

co2_ranked = co2_analysis.sort_values('pct_co2_reduction', ascending=False)

# CO2 reduction chart
# Source code on reset_index(): https://www.geeksforgeeks.org/pandas/python-pandas-dataframe-reset_index/
co2_ranked_plot = co2_ranked.reset_index()

plt.figure(figsize=(12, 5))
plt.bar(co2_ranked_plot['cluster'].astype(str), co2_ranked_plot['pct_co2_reduction'], color='blue')
plt.xlabel('Cluster')
plt.ylabel('CO2 Reduction from Solar (%)')
plt.title('Solar Panel CO2 Reduction Potential by Cluster')
plt.tight_layout()
plt.savefig(config.FIGURES_DIR / 'co2_reduction_ranking.png', dpi=150)
plt.close()