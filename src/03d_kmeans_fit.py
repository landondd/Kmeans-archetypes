import pandas as pd
from sklearn.cluster import KMeans
import config

df = pd.read_parquet(config.SCALED_FILE)

# Fit on K=13 (my final choice on K)

k_final = 13

final_km = KMeans(
    n_clusters = k_final,
    init = 'k-means++',
    n_init = 10,
    max_iter = 300,
    random_state = 42
)

final_km.fit(df)

# Assign cluster labels and save
cluster_labels = final_km.labels_
df_clean = pd.read_parquet(config.CLEAN_FILE)
df_clean['cluster'] = cluster_labels
df_clean.to_parquet(config.CLUSTERED_FILE, index=False)