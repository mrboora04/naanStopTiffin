# TEWA Summary: Random Forest & XGBoost — Delivery ETA Predictor
# NaanStop Tiffin | Post 6 | June 2026

---

## T — TOPIC: From "Is This Risky?" to "How Many Minutes?"

**Core concept:**
Post 2's `DeliveryRiskClassifier` answered a yes/no question — *is this delivery
risky?* (Logistic Regression, threshold 0.35/0.60). Post 6 asks the natural
regression follow-up: **how many minutes will it actually take?** — turning a
risk flag into a real, customer-facing ETA ("Your tiffin arrives in ~X min").

This is also the missing **Regression Tree** rung from this week's course
sequence (Classification → Decision Tree → Regression Tree → SVM → KNN →
Bias/Variance & Ensembles → Random Forest → XGBoost), finally getting its post.

Two ensemble methods, two jobs:
- **Random Forest (bagging)** trains many trees on bootstrapped samples of the
  data, then averages them. It varies the **data** per tree (same target every
  time) and primarily reduces **variance** — the instability of a single tree.
- **XGBoost (boosting)** trains trees sequentially, each one on the **residual**
  (error) of the ensemble so far. It varies the **target** per tree (same data)
  and primarily reduces **bias** — systematic error.

**The formula that makes it click for regression:**
```
F_m(x) = F_{m-1}(x) + eta * h_m(x)
residual r_i = y_i - F_{m-1}(x_i)
```
For delivery time the residual is literally *"how many minutes off was my last
guess."* Predicted 32, actual 38 → the next tree's only job is to learn that +6.
The math stopped being abstract the moment the unit became minutes.

**Current application in NaanStop Tiffin:**
Predicting `Time_taken(min)` for a delivery from rider, route, weather, traffic,
and route-batching features — so the app can show an honest ETA instead of a
generic "on its way."

**Credit:** Breiman (2001, Random Forests); Friedman (2001, Gradient Boosting
Machine); Chen & Guestrin (2016, XGBoost); IBM AI Engineering — ML with Python
(this week's bagging/boosting framing); Post 2 (`DeliveryRiskClassifier`) as the
conceptual predecessor; Post 3's `_haversine_km` for the distance feature.

---

## E — EXPERIENCE: What I Discovered

**What I learned (honest level):**
One week into the IIT Madras BS Qualifier and Module 1 of IBM's AI Engineering
course. I can explain *why* bagging and boosting work and map the formula to a
real feature — I can't yet derive XGBoost's loss function from scratch (the
second-order Taylor expansion + regularization in the Chen & Guestrin paper).
This is "I understand the mechanism," not "I reimplemented the algorithm."

**What I discovered (not from a textbook):**

1. **Boosting is a SUM, not a PICK.** I assumed boosting trained many trees and
   then *selected the best one.* It doesn't — the prediction is the **sum** of
   every tree's contribution, scaled by the learning rate η. Each tree is a
   small correction layered on the last.

2. **What varies per tree — one sentence resolved a lot of confusion.**
   Random Forest varies the **data** (bootstrap sample, same target every time).
   XGBoost varies the **target** (residuals, roughly the same data).

3. **`subsample` makes one model do both jobs ("V2 is the blend").** XGBoost's
   `subsample` + `colsample_bytree` params (Friedman 2002, Stochastic Gradient
   Boosting) train each boosting round on a random 80% of rows AND 80% of
   columns — bagging-style randomness injected *inside* the sequential process.
   So a single XGBoost model reduces variance (bagging) AND bias (boosting) at
   once. There was no need for a separate stacking/blending V3.

4. **It's not how far — it's how jammed.** The biggest surprise from the trained
   model: `Road_traffic_density` was the #1 predictor of delivery time, and
   `distance_km` ranked 8th of 11. Distance barely mattered next to traffic,
   weather, and the rider's own rating.

**Comparison matrix (the models in this week's sequence):**

| | Single Regression Tree | Random Forest Regressor | XGBoost Regressor |
|---|---|---|---|
| Mechanism | One tree, one path | Many bootstrapped trees, averaged | Sequential trees on residuals |
| Varies per tree | — | the **data** | the **target** |
| Reduces | baseline | **variance** | **bias** |
| Main risk | overfits / unstable | slower, less interpretable | overfits if η too high / too many rounds |
| Tiffin read | "one guess at ETA" | "average of 100 guesses" | "each guess corrects the last one's minute-error" |

**Credit:** Breiman, Friedman, Chen & Guestrin; scikit-learn & xgboost docs;
IBM AI Engineering course.

---

## W — WORK: What Was Actually Built

**The dataset:**
Kaggle **Food Delivery Time Prediction** dataset (`train.csv`, 45,593 rows),
copied into the repo as `archive/food_delivery_time_train.csv`. This follows the
Post 4 precedent of bundling a public Kaggle proxy dataset when the live pilot
is too small to train on. Kaggle's accompanying `test.csv` has **no**
`Time_taken(min)` labels (it's a submission set), so all evaluation uses an
honest 80/20 split of `train.csv` — 36,474 train / 9,119 held out.

**Why this dataset fixed the overfitting worry:**
The earlier candidate (Post 5's order CSV) had a median of 1 order per customer,
so per-customer features were degenerate and labels were derived from the same
aggregation — a near-circular setup. This dataset has 45k independent delivery
events with a real held-out split — clean train/test separation.

**Feature engineering:**
- `distance_km` — **reused Post 3's Haversine formula** (`_haversine_km` in
  `backend/ai/decision_tree.py`, pure-Python, no library), vectorized with numpy
  and applied to each row's Restaurant → Delivery coordinates. Same formula,
  different coordinate source.
- Numeric: `Delivery_person_Age`, `Delivery_person_Ratings`, `Vehicle_condition`,
  `multiple_deliveries` (rider carrying 0–3 orders at once — maps directly onto
  tiffin route-batching), `distance_km`.
- Categorical (passed natively, `enable_categorical=True`): `Weatherconditions`,
  `Road_traffic_density`, `Type_of_order`, `Type_of_vehicle`, `City`, `Festival`.
- Target: `"(min) 24"` strings parsed to numeric `24.0` via regex.

**Missing data — kept as signal, not imputed away:**
~4% of rows have no rating / age / traffic reading. XGBoost handles missing
*numeric* values natively (it learns a default split direction), and `"NaN"`
already appears as its own category for the categorical columns. Both are left
in rather than dropped or mean-filled.

**The model (V2 = the blend):**
```
XGBRegressor(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,          # bagging-style row sampling per round
    colsample_bytree=0.8,   # bagging-style column sampling per round
    enable_categorical=True,
    tree_method="hist",
    random_state=42,
)
```

**Smoke test results (verified, June 2026):**
```
TRAINING - DeliveryETAPredictor (XGBRegressor)
  rows trained    : 36,474
  rows held out   : 9,119
  n_estimators    : 300
  learning_rate   : 0.1
  subsample       : 0.8   (bagging-style row sampling)
  colsample_bytree: 0.8   (bagging-style column sampling)

EVALUATION - held-out 20% split
  MAE (minutes)   : 3.15

FEATURE IMPORTANCES
  Road_traffic_density      0.1938  ####################  (top)
  Delivery_person_Ratings   0.1585  ################
  Weatherconditions         0.1517  ################
  Vehicle_condition         0.1478  ###############
  multiple_deliveries       0.1125  ############
  Festival                  0.0785  ########
  Delivery_person_Age       0.0751  ########
  distance_km               0.0474  #####
  City                      0.0222  ##
  Type_of_vehicle           0.0087  #
  Type_of_order             0.0040  -

SAMPLE PREDICTIONS (held-out orders) — within ~1-3 min of actual
  actual: 44 → predicted: 45.8   (+1.8)
  actual: 41 → predicted: 42.8   (+1.8)
  actual: 39 → predicted: 35.9   (-3.1)
  actual: 38 → predicted: 40.4   (+2.4)
  actual: 38 → predicted: 39.3   (+1.3)
  actual: 22 → predicted: 22.9   (+0.9)
```

**The headline result: MAE = 3.15 minutes** on 9,119 unseen deliveries. A single
XGBoost model — doing row-bagging, column-bagging, and sequential residual
correction all at once — predicts delivery time within about three minutes.

**Iterations:**
- *V1 (done earlier in the conversation as the conceptual baseline)*: a plain
  boosting model / single-tree mental model — no internal randomness.
- *V2 (built here)*: added `subsample=0.8` + `colsample_bytree=0.8`. As discussed,
  this folds bagging INTO boosting, so V2 *is* the blend — no separate V3 stack
  needed.

**Tech stack:**
- **xgboost 3.2.0** (`XGBRegressor`) — installed into the project venv for this
  post; chosen because it matches the topic name exactly and is the production
  standard for tabular ETA prediction.
- **scikit-learn 1.8.0** — `train_test_split`, `mean_absolute_error`.
- **pandas / numpy** — feature engineering and vectorized Haversine.

**Credit:** xgboost & scikit-learn docs; Kaggle (Food Delivery Time Prediction
dataset — source link to be added at fact-check before publish); Post 3's
Haversine helper.

---

## A — ART: The Human Story

**First, an honest correction about time:**
In a ride-hailing or fast-food app, the ETA is everything — the customer is
staring at a countdown, hungry and impatient. A tiffin service is different.
Meals are planned, often subscribed, and the clock carries far less weight. Here
the minute-count matters for one reason only: *freshness* — will the food still
be hot and within the meal window when it arrives. So this delivery-time model
was never meant to be a customer-facing stopwatch. Its real job is quieter and,
I think, more useful: it is a tool *for the cook*.

**The personal issue solved — the cook leaves business on the table:**
A local cook can't see her own town. She doesn't know that, right now, fourteen
people nearby opened the app looking for lunch. She doesn't know whether, if she
started a fresh batch this minute, it could actually reach them while it's still
hot. So she plays it safe, cooks for her regulars, and a real pocket of demand
quietly goes unfed. The waste isn't just thrown-out food — it's business that
never happened, for someone who could use it.

**Design philosophy — take care of BOTH sides, or the app isn't usable:**
This is the principle that ties the whole series together. An app that only
serves customers turns the cook into a vending machine. An app that only serves
the cook ignores the person actually eating. It has to do both at once, and the
delivery-time model is what lets it. The customer side gets a freshness promise.
The cook side gets a *go / no-go signal*: "with today's traffic and weather, a
fresh batch started now reaches these fourteen people in ~28 minutes — well
inside the hot window. Cook it." The model turns scattered demand into a
decision the cook can actually act on.

**What this unlocks (the feature this post is really about):**
- **A demand nudge to the cook:** "14 people in your town are on the app looking
  for food right now. Update your inventory?" Visibility she never had before.
- **Fresh-start / almost-ready status:** the cook can broadcast "fresh batch
  starting" or "almost ready," and the ETA model confirms which customers are
  close enough to still receive it hot — so she only offers it to people she can
  genuinely serve.
- **Minimum-threshold cooking:** "Start this dish if at least X people request
  it." Demand is pooled first; the cook commits a fresh batch only when it's
  worth her time — more business, zero gambling on waste.

**Beauty & craft — why the model's honesty matters here:**
The diagnostics found the model is accurate in the middle (3.17 min average miss,
82% of the variance explained) but turns *optimistic on the slow deliveries* —
it under-predicts the genuinely long runs. For a customer countdown that would be
a flaw. For the cook's go/no-go it becomes a design rule: only let her commit a
fresh batch when the predicted time fits *comfortably* inside the freshness
window, and pad the uncertain cases (Jam traffic, long distance, missing traffic
data — where error doubles). Better she passes on a risky order than serves a
neighbour a cold one. The model's weaknesses became the product's caution.

**Personal voice & the thread back to the cook:**
Post 6 rhymes with everything before it. Post 3's Surplus Matcher fought food
waste. Post 5 handed clusters to the cook so *she* decided whether to cook
extra. Same value here: the machine does the arithmetic — who's nearby, what's
the traffic, can it arrive fresh — so one person doesn't have to hold the whole
town in her head. But the decision to cook, and the trust with the neighbour she
feeds, stay with her. The AI is the messenger. The cook holds the power.

**Impact & meaning:**
Done right, this is a tiny home kitchen getting something the big platforms never
gave it: a way to *grow*. The cook sees real demand, cooks fresh into it without
fear of waste, and serves more people. The customer gets hot food and an honest
"yes, we can reach you." Both sides win at the same time — which is the only way
a neighbourhood app like this is worth building at all.

**What's next (the weaknesses, stated as a roadmap):**
The model still can't explain a genuine 50-minute delivery — nothing in its
features says "this one will drag." A future post adds the missing signal:
kitchen prep time, time-of-day rush, and how many orders are stacked on the
rider. And traffic, the strongest feature, should never reach the model as
`NaN`.

**Credit:** The IBM AI Engineering course (this week's bagging/boosting unit);
the Kaggle Food Delivery Time dataset that stood in for our pilot; and the local
cooks this whole project is built around.

---

## Artefacts & Links

| File | Purpose |
|---|---|
| [delivery_eta_xgboost.py](../backend/ai/delivery_eta_xgboost.py) | `DeliveryETAPredictor` (XGBRegressor, subsample=0.8) |
| [smoke_test_xgboost_eta.py](../backend/smoke_test_xgboost_eta.py) | Full end-to-end test (ran [OK], MAE 3.15) |
| [food_delivery_time_train.csv](../archive/food_delivery_time_train.csv) | Kaggle training data (45,593 delivery events) |
| [decision_tree.py](../backend/ai/decision_tree.py) | Source of the reused `_haversine_km` formula |

**Post 6 of the NaanStop Tiffin LinkedIn series.**
Previous: Post 5 — K-Means Clustering (Regulars vs Irregulars)
Next: Post 7 — TBD
