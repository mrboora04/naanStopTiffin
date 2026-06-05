# TEWA Summary: KNN Classification — Guilt by Association

---

## T — TOPIC: Guilt by Association (KNN Classification)

**Core concept:**
K-Nearest Neighbors (KNN) is a supervised machine learning algorithm based on a simple, intuitive premise: "Show me who your friends are, and I will tell you who you are." It classifies unlabeled data points by looking at the known labels of their closest neighbors. 

**Historical context:**
The algorithm fundamentally balances the Bias-Variance tradeoff through the hyperparameter K (number of neighbors). A low K leads to high variance (overfitting), while a high K leads to high bias (oversmoothing). Our original testing of this concept used a Telecom customer dataset to classify users into overlapping service groups by finding the sweet spot at K=9.

**Current application in NaanStop Tiffin:**
We are applying KNN to the "Lone Birds"—users who have an account but aren't on a strict Mon-Fri tiffin subscription. Unlike regular subscribers who don't even open the app because their food just arrives, Lone Birds order ad-hoc. 

**Implementation strategies:**
- *Smart Implementation (The "Usual" Time-Based Nudge)*: This is our current focus. If a user typically orders lunch at 11:30 AM every weekday, and today it's 11:50 AM with no order, we use KNN clustering to confirm their "usual" behavior and trigger a notification: *"Your usual lunch is available today 🍱"* (High conversion).

**Future Roadmap (Idea Book):**
- *Cook Meal Rotation & Insights*: Reverse-KNN to tell the cook: *"50% of your audience eats spicy food—add a spicy dish next week."*
- *Budget Discovery*: A budget bar filter for student workers, clustering them with matching cooks.
- *Seasonal Recommendations*: Recommending new cooks based on what similar Lone Bird users are exploring.

**Credit:** 
Foundational principles of supervised learning and the Telecom customer dataset baseline.

---

## E — EXPERIENCE: What I Discovered

**What I learned:**
KNN is perfectly suited for irregular, ad-hoc behaviors where traditional rule-based logic fails. While subscribers are highly predictable, "Lone Birds" have hidden, overlapping patterns. By looking at their K-Nearest Neighbors, we can predict their typical order time even if their personal order history is sparse.

**Original insight:**
The most powerful use of KNN isn't just recommending *what* to eat, but *when* to remind them. Combining the KNN clustering with a time-delay trigger turns a generic push notification into a highly contextual nudge.

**Comparison:**
- *Decision Tree (Surplus Matcher)*: Great for explicit, hard rules.
- *KNN (Time-Based Nudge)*: Superior for implicit discovery and pattern matching based on historical timing.

**Credit:**
Machine learning community (collaborative filtering concepts). 
