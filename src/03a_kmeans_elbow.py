import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import config

df = pd.read_parquet(config.SCALED_FILE)

# Make sure the size of the data is correct and we have all columns

##print("Shape: ", df.shape)
##print('Columns: ', df.columns.tolist())

inertias = []
k_range = range(2, 31)

for k in k_range:
    km = KMeans(
        n_clusters = k,
        init = 'k-means++',
        n_init = 10,
        max_iter = 300,
        random_state = 42
    )
    km.fit(df)
    inertias.append(km.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(list(k_range), inertias, color='blue', marker='o', linestyle='-', markersize=8)
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Inertia (Within-Cluster Sum of Squares)')
plt.title('Elbow Plot — K-means on EPC Data')
plt.xticks(list(k_range))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(config.FIGURES_DIR / 'elbow_plot.png', dpi=150)
plt.show()

print("All inertias: ", inertias)

