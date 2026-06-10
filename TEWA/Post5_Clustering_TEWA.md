---
name: Post5-Clustering
description: TEWA narrative for Post 5 of IBM Coursera Machine Learning with Python
---

# When Perfect Math Fails: Why I Abandoned K-Means for Physical Advertising (And What I Used Instead)

As a developer building the **naanStopTiffin** food delivery app, I had an idea: What if I used Machine Learning to find the exact geographic locations to place physical ads? 

I had delivery coordinates, customer cuisine preferences, and I was deep into the IBM Machine Learning course on Coursera. It was time to use Unsupervised Learning—specifically **K-Means Clustering**—to find my advertising "Hotspots."

Here is how I built it, why it completely failed in the real world, and the crucial lesson I learned about operational machine learning.

### T — The Concept: The K-Means Promise
K-Means clustering is a powerful unsupervised algorithm that discovers hidden groupings in messy, unlabeled data. 

It is an **iterative, centroid-based algorithm**. You give it a number ($K$) of "centroids" (center points). It drops those points onto your data map and loops through a simple process:
1. **Initialize:** It starts by randomly placing the $K$ centroids.
2. **Assign:** Every data point connects to the nearest centroid.
3. **Update:** The centroid recalculates its position, moving to the exact mathematical center of its new cluster.
4. **Repeat:** It loops through assigning and updating until the centroids stop moving (convergence).

**Why can't it just calculate the center once?** 
Because of a mathematical "Chicken and Egg" problem! You can't calculate the exact center of a group until you know *which* customers are in the group. But you can't know which customers are in the group until you know where the center is. That's why it has to iteratively shuffle the customers and move the center until no one switches teams.

### E — What I Discovered: Unsupervised Quirks & The "Empty Field"
Building this out taught me the fundamental difference between Supervised and Unsupervised learning. 
In supervised learning, you have a "Test" dataset to see if your model is right. **In K-Means, there are no right answers and no test sets.** You have to rely on mathematical scoring (like the Silhouette Score) and sheer human business logic to validate the clusters.

I also made a massive discovery: K-Means isn't just for 2D maps. 
In Barrie, a customer getting a burrito has a very different profile than someone going to Mumbai Central. I learned that K-Means is **multi-dimensional**. I can feed the algorithm 4 dimensions: Latitude, Longitude, Customer Occupation, and Cuisine Preference. It calculates the distance across *all* those variables simultaneously to find the perfect center of a specific demographic.

But there is a catch. I discovered what I call the **"Empty Field" Problem**. 
Because K-Means calculates the exact mathematical mean, the theoretical "perfect center" of a customer zone might literally land in the middle of a residential house, a farm field, or a lake! 

*The Solution:* I realized the K-Means centroid is just an *anchor*. To make it actionable, you must take that theoretical coordinate and cross-reference it with a Map API to find the nearest valid commercial plaza (like one of the two Walmarts in Barrie or a Tim Hortons) to actually place the physical ads.

### W — The Pivot: Where K-Means Actually Shines
I realized I was using the wrong tool for the job. Geographic ad placement is a network constraint problem, not a simple clustering problem.

Instead of abandoning the algorithm, I pivoted. I stopped trying to cluster physical map locations, and instead clustered **user behavior**. 

The core business model of a Tiffin app is long-term, high-frequency subscriptions. But I also have a secondary market: people who order last-minute just because the delivery driver happens to be nearby with extra food. 

I loaded a real food delivery dataset, used Pandas `groupby` to engineer two features per customer—**Order Frequency** and **Average Spend**—and plotted them on a 2D graph. I didn't write any IF/THEN rules. I let K-Means calculate the Euclidean distances and find the centroids.

First, I ran the **Elbow Method** to mathematically confirm K=2 was optimal. The WCSS (Within-Cluster Sum of Squares) curve dropped sharply from K=1 to K=2, then flattened — proving two clusters was the natural shape of the data.

Without any labeled data, the algorithm perfectly separated the customers into two distinct clusters (Silhouette Score: 0.440):
1. **The Regulars** (navy): Centroid at **$22.60 avg spend | 2.0 orders** — consistent, higher-value subscribers.
2. **The Irregulars** (red): Centroid at **$11.90 avg spend | 1.3 orders** — occasional buyers who grab a meal when something is available.


### A — The Art: Empowering the Local Cook
Why does clustering "Regulars" and "Irregulars" matter? Because it solves a real human problem.

If the local cook doesn't prepare the food, why are we even making this app? Who will eat breakfast, lunch, or dinner? The goal of my machine learning wasn't to build a massive, top-down automated tech company. The goal was to give power back to the local cooks.

By feeding this clustering data directly to the cooks, *they* get to review it. The app doesn't force them to cook extra food. But when a local cook looks at the data and sees the "Irregulars" cluster growing with daily requests, *they* can make the decision to start cooking extra. 

The machine learning is just the messenger. It analyzes the town so one single person doesn't have to do it all by themselves. But at the end of the day, the local cook holds the real power.

---
*Check out the theoretical Python clustering code in my repository!*
