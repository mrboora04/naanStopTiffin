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

---

## W — WORK: What Was Actually Built

**Implementation process:**
We are building a `LoneBirdNudgePredictor` using Python and scikit-learn. The core process involves taking our existing `Delivery` records, filtering for ad-hoc orders, and extracting the exact order time (in minutes past midnight) alongside the day of the week to train the model. 

**Files & Architecture (Planned):**
- `backend/models/delivery.py`: Adapting the schema to track `ordered_at` (DateTime) so we know the exact minute the ad-hoc order was placed.
- `backend/models/member.py`: Identifying "Lone Birds" by checking `plan_id == null` and adding a `last_nudge_sent` timestamp to prevent push notification spam.
- `backend/ai/knn.py`: The algorithm utilizing `KNeighborsRegressor`. It maps historical order times to find the "usual" time window for the user or their nearest demographic neighbors.
- `backend/smoke_test_knn.py`: A simulated environment using synthetic Lone Bird records to verify that the 20-minute delay trigger correctly fires at 11:50 AM for an 11:30 AM regular.

**Tech stack & Tools:**
- **scikit-learn (`KNeighbors`)**: Chosen for its simplicity in calculating proximity. It perfectly maps to our "guilt by association" core concept.
- **SQLAlchemy**: For cleanly querying and aggregating the ad-hoc `Delivery` records from our SQLite/Postgres database.

**Iterations & Operational Rules:**
- *V1 (Simple Average)*: Initially, one might try just averaging a user's past order times. But if a user only ordered once, the average is useless.
- *V2 (KNN Clustering)*: By using KNN, we solve the cold-start problem. If a user's history is sparse, the algorithm looks at their "neighbors" (users with similar behaviors) to predict the likely order time.
- *Operational Constraints (The Reality Check)*: We added strict rules overriding the AI. We DO NOT send the nudge if the cook is done cooking or the delivery driver has already left the store. A nudge is only useful if we can actually fulfill the order.
- *Feature Engineering*: We track if a "Lone Bird" is an *offer-hunter* (only orders with discounts) or a *visual scroller* (orders by looking at images). This helps tailor the push notification's content.

**Data & Assets (The LinkedIn Proof):**
Because our pilot doesn't have thousands of users yet, we can leverage public datasets to build and prove the prototype for a LinkedIn showcase. The **Zomato Delivery Operations Analytics** or **Uber Eats USA Restaurants** datasets on Kaggle are perfect proxies to train the model on real-world order times and user clustering before deploying it to our live app.

**Credit:**
scikit-learn documentation; Kaggle open datasets (Zomato/Uber Eats) for training data.

**Smoke test results (verified, June 2026):**

```
  [Model 1] LoneBirdTimeNudge
    status         : trained
    rows trained   : 895 (Delivered orders from Kaggle)
    K              : 9
    MAE (minutes)  : 17.97

  [Model 2] WildcardRecommender
    status         : trained
    user segments  : 11
    K neighbours   : 5

  MODEL 1 — TIME-BASED NUDGE (11:50 AM run)
    [SEND NUDGE]  Arjun (Student, 22)       -> "Your usual lunch is available today!"
    [SEND NUDGE]  Priya (Professional, 34)  -> "Your usual lunch is available today!"
    [SKIP]        Sam (Already ordered)     -> Already ordered today
    [SEND NUDGE]  Meera (Budget hunter, 45) -> "Your usual lunch is available today!"
    [SKIP]        Raj (10:00 AM)            -> Too early — not past window yet
    [SEND NUDGE]  Nisha (Explorer, 27)      -> "Your usual lunch is available today!"
    Nudges queued: 4 / 6 users

  MODEL 2 — WILDCARD RECOMMENDER (weekly run)
    Arjun   -> suggest Cafe      17.6% neighbour match
    Priya   -> suggest Fast Food 16.1% neighbour match
    Meera   -> suggest Cafe      17.0% neighbour match
    Raj     -> suggest Fast Food 19.0% neighbour match
    Nisha   -> [SKIP] Has tried all cuisine types — great explorer!
```

---

## Artefacts & Links

| File | Purpose |
|---|---|
| [knn.py](../backend/ai/knn.py) | Core KNN models (LoneBirdTimeNudge + WildcardRecommender) |
| [smoke_test_knn.py](../backend/smoke_test_knn.py) | Full end-to-end test (ran [OK]) |
| [migrate_add_knn_features.py](../backend/migrate_add_knn_features.py) | DB migration (ran [OK]) |
| [daily_food_delivery_orders.csv](../archive/daily_food_delivery_orders.csv) | Kaggle training data (895 delivered orders) |
| [future-plans.md](../curry-admin/docs/future-plans.md) | KNN future features (Cook Rotation, Budget Bar, Seasonal Recs) |

**Post 4 of the NaanStop Tiffin LinkedIn series.**
Previous: Post 3 — Decision Tree (Surplus Food Matcher)
Next: Post 5 — TBD

---

## A — ART: The Human Story

**The personal issue solved:**
If you search Reddit or X (Twitter) for food delivery complaints, you'll see a massive recurring theme: *Decision Paralysis and the Food Rut*. People complain about scrolling on Uber Eats for 30 minutes just to end up ordering the exact same meal they always get. The mental toll of deciding "what to eat" completely defeats the convenience of the app. 

**Design philosophy:**
We are solving the "Food Rut" with a personal touch. While our technical "Work" focuses on knowing *when* you want your usual, our "Art" is knowing *how* to break you out of your comfort zone safely. We use KNN to find your "neighbors," and once a week, we gently recommend an "out of the box" wildcard dish that your cluster loves, but you haven't tried yet. 

**Beauty & craft:**
The craft lies in the subtlety. We introduce this wildcard dish softly. If you ignore it, we back off so you never get irritated. If you try it, it might just become part of your regular rotation. We don't shove promoted, expensive restaurants in your face like traditional apps; instead, we act like a trusted friend saying, "Hey, I know you usually get the butter chicken, but people with your exact taste profile are obsessed with this new paneer dish today. Want to try it?"

**Impact:**
It transforms the app from a transactional ordering utility into a personal culinary guide. It cures the Reddit-famous "scrolling fatigue" by offering a highly personalized, out-of-the-box suggestion right when you're feeling adventurous, keeping the menu fresh and exciting.

**Credit:**
The countless Reddit and X threads of people suffering from menu fatigue and 30-minute scrolling sessions.
