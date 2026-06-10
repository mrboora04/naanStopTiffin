# %% [markdown]
# # Discovering Hotspots with Spatial Clustering (K-Means)
# This notebook demonstrates how to use K-Means clustering on geographic coordinates 
# (Latitude & Longitude) to group Tiffin app drop-off locations. 
# We'll use these clusters to find optimal physical advertising hotspots (centroids).

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set aesthetic style
sns.set_theme(style="whitegrid")

# %% [markdown]
# ## 1. Generate Mock Drop-off Data
# We will generate synthetic GPS coordinates representing Tiffin deliveries around a city.

# %%
# Setting a random seed for reproducibility
np.random.seed(42)

# Simulating 3 main "neighborhoods" where orders are popular
# Neighborhood 1 (Downtown)
lat_1 = np.random.normal(43.6532, 0.02, 150)
lon_1 = np.random.normal(-79.3832, 0.02, 150)

# Neighborhood 2 (Suburbs)
lat_2 = np.random.normal(43.7000, 0.015, 100)
lon_2 = np.random.normal(-79.4500, 0.015, 100)

# Neighborhood 3 (University Area)
lat_3 = np.random.normal(43.6600, 0.01, 200)
lon_3 = np.random.normal(-79.3400, 0.01, 200)

# Combine into a single DataFrame
lats = np.concatenate([lat_1, lat_2, lat_3])
lons = np.concatenate([lon_1, lon_2, lon_3])

df = pd.DataFrame({'Latitude': lats, 'Longitude': lons})

print(f"Total delivery drops: {len(df)}")
df.head()

# %% [markdown]
# ## 2. Visualize the Raw Data
# Before clustering, let's see what the raw drop-off locations look like on a scatter plot.

# %%
plt.figure(figsize=(10, 6))
plt.scatter(df['Longitude'], df['Latitude'], alpha=0.6, edgecolors='w', s=50)
plt.title("Raw Delivery Drop-off Locations (Latitude vs Longitude)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# %% [markdown]
# ## 3. The "K" Tradeoff - Finding the Optimal Number of Clusters
# We use the **Elbow Method** to calculate the Within-Cluster Sum of Squares (WCSS) 
# and find the perfect $K$ (number of centroids).

# %%
# Feature Scaling: K-Means is a distance-based algorithm, so scaling is critical.
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df)

wcss = []
max_k = 10

for k in range(1, max_k + 1):
    # The Iterative Engine: Initialize, Assign, Update, Repeat
    kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(scaled_features)
    wcss.append(kmeans.inertia_) # inertia_ is the WCSS

# Plot the Elbow Graph
plt.figure(figsize=(8, 5))
plt.plot(range(1, max_k + 1), wcss, marker='o', linestyle='--')
plt.title('The Elbow Method (Optimal K)')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('WCSS')
plt.xticks(range(1, max_k + 1))
plt.show()

# %% [markdown]
# **Observation:** The "elbow" bends sharply at $K=3$. This means 3 centroids provide 
# the most efficient grouping without over-segmenting the data.

# %% [markdown]
# ## 4. Run K-Means and Find the Centroids
# Now we apply $K=3$ to find our exact Advertising Hotspots.

# %%
# Initialize and fit the model
optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, init='k-means++', random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(scaled_features)

# The centroids are in scaled format, we need to inverse_transform them back to Lat/Lon
centroids_scaled = kmeans.cluster_centers_
centroids_actual = scaler.inverse_transform(centroids_scaled)

print("Optimal Advertising Hotspots (Centroids):")
for i, coord in enumerate(centroids_actual):
    print(f"Hotspot {i+1}: Latitude {coord[0]:.4f}, Longitude {coord[1]:.4f}")

# %% [markdown]
# ## 5. Visualize the Clusters & Advertising Hotspots
# Let's plot the clustered points and clearly mark our $K$ centroids.

# %%
plt.figure(figsize=(10, 6))

# Plot the data points colored by cluster
sns.scatterplot(x='Longitude', y='Latitude', hue='Cluster', data=df, palette='viridis', s=50, alpha=0.6)

# Plot the Centroids as massive red stars
plt.scatter(centroids_actual[:, 1], centroids_actual[:, 0], 
            s=400, c='red', marker='*', edgecolor='black', label='Advertising Centroid')

plt.title("Customer Segments & Advertising Hotspots (K=3)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.show()

# %% [markdown]
# ### Conclusion
# We successfully grouped 450 unlabeled delivery drop-offs into 3 distinct geographic zones. 
# The massive red stars (Centroids) represent the exact mathematical center of customer density. 
# By finding industrial plazas near these 3 specific coordinates, we can optimize our physical 
# advertising budget for maximum word-of-mouth growth!
