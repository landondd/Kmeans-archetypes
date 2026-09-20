import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import config

df = pd.read_parquet(config.SCALED_FILE)

# Inertia values copy+paste from 03.1 K-means - Elbow.py to hold, if needed
inertias = [270361843.254385, 242669697.6606861, 225140004.85928783, 206662977.097107,
            191445399.1287914, 175086133.21707377, 158902747.82185686, 143264264.29836607,
            128186849.01408273, 113223942.19111839, 97415550.08915465, 82453274.93055692,
            73339533.24320635, 69550643.21439093, 64831402.49407196, 60983628.50461597,
            57171583.139054745, 54914715.010602914, 51429135.74914782, 48929223.525105186,
            46585488.70316902, 44982420.586278945, 42443413.39244404, 41686992.833479695,
            39907209.31494089, 38586358.75824764, 37350583.61926396, 36353151.48107267,
            35208009.772015676]

# Silhouette Scores
# Fixed 50,000 row sample for silhouette scoring

np.random.seed(42)
# Random sample source code here: https://stackoverflow.com/questions/58414272/how-does-numpy-random-choice-work-with-replacement
sample_records = np.random.choice(len(df), size=50000, replace=False)
df_sil_sample = df.iloc[sample_records]

silhouette_scores = []
k_range = range(2, 31)

for k in k_range:
    km = KMeans(
        n_clusters=k,
        init='k-means++',
        n_init=10,
        max_iter=300,
        random_state=42
    )
    labels = km.fit_predict(df)
    sil_labels = labels[sample_records]
    score = silhouette_score(df_sil_sample, sil_labels)
    silhouette_scores.append(score)

print("silhouette scores: ", silhouette_scores)

