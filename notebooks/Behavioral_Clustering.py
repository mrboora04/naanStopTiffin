"""
Behavioral Clustering — naanStopTiffin
======================================
Post 5: IBM Coursera "Machine Learning with Python"
Topic: Unsupervised Learning / K-Means Clustering

This script loads real food delivery data from Kaggle, engineers
Order Frequency and Average Spend per customer, then uses K-Means
to discover two natural behavioral clusters:
  - The Regulars   : long-term, high-frequency subscribers
  - The Irregulars : ad-hoc buyers who order when extra food is available
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ──────────────────────────────────────────────
# 1. DATA INGESTION
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "Food Order Delivery Time (1).csv")

df_raw = pd.read_csv(CSV_PATH)
print("[OK] Data loaded:", df_raw.shape)
print(df_raw.head(3))

# ──────────────────────────────────────────────
# 2. FEATURE ENGINEERING
#    Transform raw transactions → one row per customer
#    Features:
#      - order_frequency  : how many times they ordered
#      - avg_spend        : mean cost per order
# ──────────────────────────────────────────────
customer_profiles = (
    df_raw.groupby("customer_id")
    .agg(
        order_frequency=("order_id", "count"),
        avg_spend=("cost_of_the_order", "mean"),
    )
    .reset_index()
)

print(f"\n[OK] Customer profiles built: {len(customer_profiles)} unique customers")
print(customer_profiles.describe())

# ──────────────────────────────────────────────
# 3. DATA SCALING
#    K-Means is distance-based. Without scaling,
#    a $30 spend dominates a 3-order frequency.
# ──────────────────────────────────────────────
features = customer_profiles[["order_frequency", "avg_spend"]].values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# ──────────────────────────────────────────────
# 4. ELBOW METHOD — find the optimal K
# ──────────────────────────────────────────────
inertia = []
K_range = range(1, 9)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(features_scaled)
    inertia.append(km.inertia_)

fig_elbow, ax_elbow = plt.subplots(figsize=(8, 4))
ax_elbow.plot(K_range, inertia, marker="o", color="#E94560", linewidth=2)
ax_elbow.set_title("Elbow Method — Optimal K for Tiffin Behavioral Clustering",
                   fontsize=13, fontweight="bold")
ax_elbow.set_xlabel("Number of Clusters (K)")
ax_elbow.set_ylabel("Inertia (WCSS)")
ax_elbow.axvline(x=2, color="#0F3460", linestyle="--", alpha=0.6, label="Chosen K=2")
ax_elbow.legend()
ax_elbow.grid(alpha=0.3)
fig_elbow.tight_layout()
elbow_path = os.path.join(BASE_DIR, "notebooks", "elbow_method.png")
fig_elbow.savefig(elbow_path, dpi=150)
print(f"\n[OK] Elbow chart saved -> {elbow_path}")

# ──────────────────────────────────────────────
# 5. K-MEANS CLUSTERING  (K = 2)
#    Cluster 0 → The Regulars
#    Cluster 1 → The Irregulars
# ──────────────────────────────────────────────
K = 2
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
customer_profiles["cluster"] = kmeans.fit_predict(features_scaled)

# Silhouette score (how tight / well-separated are the clusters?)
sil_score = silhouette_score(features_scaled, customer_profiles["cluster"])
print(f"\n[OK] K-Means complete | Silhouette Score: {sil_score:.3f}  (1.0 = perfect)")

# Map cluster IDs → human-readable labels
# Identify which cluster has higher average frequency → "The Regulars"
cluster_means = customer_profiles.groupby("cluster")["order_frequency"].mean()
regular_cluster = cluster_means.idxmax()
irregular_cluster = 1 - regular_cluster  # only 2 clusters

label_map = {regular_cluster: "The Regulars", irregular_cluster: "The Irregulars"}
customer_profiles["label"] = customer_profiles["cluster"].map(label_map)

print("\nCluster sizes:")
print(customer_profiles["label"].value_counts())

# Centroids — un-scale them back to original units for readability
centroids_scaled = kmeans.cluster_centers_
centroids_original = scaler.inverse_transform(centroids_scaled)

# ──────────────────────────────────────────────
# 6. VISUALIZATION — the 2D Scatter (the sketch!)
# ──────────────────────────────────────────────
PALETTE = {
    "The Regulars":   "#0F3460",   # deep navy
    "The Irregulars": "#E94560",   # vivid red
}

fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#F7F9FC")
ax.set_facecolor("#F7F9FC")

sns.scatterplot(
    data=customer_profiles,
    x="avg_spend",
    y="order_frequency",
    hue="label",
    palette=PALETTE,
    alpha=0.65,
    s=60,
    edgecolor="white",
    linewidth=0.4,
    ax=ax,
)

# Plot centroids as big red stars
for i, (cx, cy) in enumerate(zip(centroids_original[:, 1], centroids_original[:, 0])):
    ax.scatter(
        cx, cy,
        marker="*",
        s=600,
        color="#FFD700",        # gold star
        edgecolors="#222",
        linewidth=0.8,
        zorder=5,
        label="Centroid" if i == 0 else "",
    )
    ax.annotate(
        f"Centroid\n${cx:.1f} avg | {cy:.1f}x orders",
        xy=(cx, cy),
        xytext=(cx + 0.5, cy + 0.3),
        fontsize=8,
        color="#333",
        arrowprops=dict(arrowstyle="->", color="#888", lw=0.8),
    )

# Labels & styling
ax.set_title(
    "naanStopTiffin — Behavioral Clustering\nFinding The Regulars vs The Irregulars",
    fontsize=14, fontweight="bold", pad=14,
)
ax.set_xlabel("Average Spend per Order ($)", fontsize=11)
ax.set_ylabel("Order Frequency (# of Orders)", fontsize=11)
ax.grid(alpha=0.2, linestyle="--")

# Custom legend
reg_patch   = mpatches.Patch(color=PALETTE["The Regulars"],   label="The Regulars")
irreg_patch = mpatches.Patch(color=PALETTE["The Irregulars"], label="The Irregulars")
star_patch  = plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
                          markersize=14, label="Centroid", markeredgecolor="#222")
ax.legend(handles=[reg_patch, irreg_patch, star_patch], loc="upper right", framealpha=0.85)

# Silhouette watermark
ax.text(
    0.01, 0.01,
    f"Silhouette Score: {sil_score:.3f}",
    transform=ax.transAxes,
    fontsize=9, color="#555", style="italic"
)

fig.tight_layout()
cluster_path = os.path.join(BASE_DIR, "notebooks", "behavioral_clusters.png")
fig.savefig(cluster_path, dpi=150)
print(f"\n[OK] Cluster chart saved -> {cluster_path}")

plt.show()
print("\nDone! Two charts saved to naanStopTiffin/notebooks/")
