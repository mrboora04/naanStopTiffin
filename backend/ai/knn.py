"""
knn.py  —  NaanStop Tiffin | KNN "Lone Bird" Predictor
──────────────────────────────────────────────────────────────────────────────
Two models powered by K-Nearest Neighbors:

  Model 1 — LoneBirdTimeNudge
      "Your usual lunch is available today!"
      Trains on historical order times + day-of-week patterns.
      At runtime: if the user is 20+ minutes past their predicted order
      window and hasn't ordered yet, trigger the nudge.

  Model 2 — WildcardRecommender
      "People with your taste profile love this dish this week."
      Trains on user cuisine preferences and order values.
      Once a week: find the closest neighbours and surface a highly-rated
      cuisine type the user has NOT tried yet.

Data source: archive/daily_food_delivery_orders.csv (Kaggle)
  Columns used:
    order_date, delivery_time_minutes  -> order-time proxy features
    customer_age, order_value          -> budget / demographic clustering
    restaurant_type                    -> cuisine preference
    order_status                       -> quality filter (Delivered only)
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.neighbors import KNeighborsRegressor, NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ── Path helpers ──────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
_ROOT   = os.path.abspath(os.path.join(_HERE, "..", ".."))
DATA_PATH = os.path.join(_ROOT, "archive", "daily_food_delivery_orders.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Shared data loader
# ─────────────────────────────────────────────────────────────────────────────
def _load_data() -> pd.DataFrame:
    """
    Load and clean the Kaggle delivery dataset.
    We keep only 'Delivered' orders so the KNN learns from successful
    interactions, not cancellations.
    """
    df = pd.read_csv(DATA_PATH)
    df = df[df["order_status"] == "Delivered"].copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["day_of_week"] = df["order_date"].dt.dayofweek   # 0=Mon, 6=Sun
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 1 — LoneBirdTimeNudge
# ─────────────────────────────────────────────────────────────────────────────
class LoneBirdTimeNudge:
    """
    Predicts the expected order-time window for a Lone Bird user.

    The Kaggle data does not have exact timestamps, so we treat
    delivery_time_minutes as a proxy for order urgency/time-of-day
    (faster deliveries tend to cluster around peak lunch/dinner windows).

    In production, this trains on real ordered_at timestamps from the
    deliveries table. For the LinkedIn demo, we use the Kaggle proxy.

    NUDGE RULE:
      If current_time > predicted_order_window_end AND user hasn't ordered
      today AND last_nudge_sent is not today → SEND NUDGE.
    """

    NUDGE_DELAY_MINUTES = 20   # How many minutes past the window before nudging
    K = 9                      # Optimal K found from Telecom baseline experiment

    def __init__(self):
        self.model   = KNeighborsRegressor(n_neighbors=self.K, metric="euclidean")
        self.scaler  = StandardScaler()
        self.trained = False
        self.status  = "untrained"

    def train(self, df: pd.DataFrame):
        """
        Features: [day_of_week, order_value, delivery_distance_km]
        Target  : delivery_time_minutes (proxy for order-time urgency)
        """
        feature_cols = ["day_of_week", "order_value", "delivery_distance_km"]
        X = df[feature_cols].values
        y = df["delivery_time_minutes"].values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.trained = True
        self.status  = "trained"

        self.train_n  = len(df)
        self.k_used   = self.K

        # In-sample accuracy proxy: mean absolute error in minutes
        y_pred    = self.model.predict(X_scaled)
        self.mae  = float(np.mean(np.abs(y - y_pred)))

    def predict_window(self, day_of_week: int, order_value: float, distance_km: float) -> float:
        """Returns predicted order-time window (minutes from midnight proxy)."""
        if not self.trained:
            raise RuntimeError("Model not trained yet.")
        X = np.array([[day_of_week, order_value, distance_km]])
        X_scaled = self.scaler.transform(X)
        return float(self.model.predict(X_scaled)[0])

    def should_nudge(
        self,
        user_id: str,
        day_of_week: int,
        avg_order_value: float,
        avg_distance_km: float,
        minutes_since_midnight: int,
        has_ordered_today: bool,
        last_nudge_date,
    ) -> dict:
        """
        Core nudge decision logic.
        Returns a dict with decision + reasoning.
        """
        if has_ordered_today:
            return {"nudge": False, "reason": "Already ordered today"}

        today = datetime.now().date()
        if last_nudge_date and last_nudge_date == today:
            return {"nudge": False, "reason": "Nudge already sent today"}

        predicted_window = self.predict_window(day_of_week, avg_order_value, avg_distance_km)
        threshold = predicted_window + self.NUDGE_DELAY_MINUTES

        # Only nudge if we're PAST the threshold, not before the window
        if minutes_since_midnight < predicted_window:
            return {
                "nudge":            False,
                "reason":           "Too early — user's order window hasn't started yet",
                "predicted_window": round(predicted_window, 1),
            }

        if minutes_since_midnight >= threshold:
            return {
                "nudge":            True,
                "reason":           "Past predicted order window",
                "predicted_window": round(predicted_window, 1),
                "threshold":        round(threshold, 1),
                "current_time_min": minutes_since_midnight,
                "message":          "Your usual lunch is available today!",
            }
        return {
            "nudge":            False,
            "reason":           "Too early — not past window yet",
            "predicted_window": round(predicted_window, 1),
        }

    def summary(self) -> dict:
        return {
            "model":       "LoneBirdTimeNudge",
            "status":      self.status,
            "data_source": "Kaggle daily_food_delivery_orders.csv",
            "rows_trained": getattr(self, "train_n", 0),
            "k":           self.K,
            "mae_minutes": round(getattr(self, "mae", 0), 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 2 — WildcardRecommender
# ─────────────────────────────────────────────────────────────────────────────
CUISINE_TYPES = ["Indian", "Chinese", "Italian", "Cafe", "Fast Food", "Bakery"]

class WildcardRecommender:
    """
    Finds a user's K nearest neighbours based on cuisine preferences
    and budget, then surfaces a popular cuisine from the neighbours
    that the user has NOT tried yet.

    This solves the Reddit "Food Rut" problem documented in the TEWA A section.

    WILDCARD RULE:
      Once a week: find the K nearest neighbours of this user (by age +
      budget + cuisine history vector). Of the cuisines their neighbours
      love, pick one the user hasn't ordered yet. Serve it softly.
      If ignored, back off (don't send again for 2 weeks).
    """

    K = 5

    def __init__(self):
        self.model   = NearestNeighbors(n_neighbors=self.K + 1, metric="euclidean")
        self.scaler  = StandardScaler()
        self.le      = LabelEncoder()
        self.le.fit(CUISINE_TYPES)
        self.trained = False
        self.status  = "untrained"
        self._user_profiles: pd.DataFrame = None

    def _build_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate per 'customer_age' bucket (proxy for user segment) to build
        preference vectors.  In production this would be per real user_id.
        """
        # Bin age into 5-year buckets to create user-like segments
        df = df.copy()
        df["age_bucket"] = (df["customer_age"] // 5) * 5

        # Cuisine one-hot pivot per age bucket
        cuisine_dummies = pd.get_dummies(df["restaurant_type"])
        df = pd.concat([df, cuisine_dummies], axis=1)

        cuisine_cols = [c for c in CUISINE_TYPES if c in df.columns]
        profile = df.groupby("age_bucket").agg(
            avg_order_value        = ("order_value", "mean"),
            total_orders           = ("order_id", "count"),
            **{c: (c, "sum") for c in cuisine_cols}
        ).reset_index()

        # Convert cuisine counts to proportions (taste profile vector)
        row_total = profile[cuisine_cols].sum(axis=1).replace(0, 1)
        for c in cuisine_cols:
            profile[c] = profile[c] / row_total

        return profile

    def train(self, df: pd.DataFrame):
        profiles   = self._build_profiles(df)
        self._user_profiles = profiles

        cuisine_cols = [c for c in CUISINE_TYPES if c in profiles.columns]
        feature_cols = ["avg_order_value"] + cuisine_cols
        X = profiles[feature_cols].values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)

        self.trained     = True
        self.status      = "trained"
        self.train_n     = len(profiles)
        self._feature_cols = feature_cols
        self._cuisine_cols = cuisine_cols

    def recommend_wildcard(self, age: int, avg_spend: float, tried_cuisines: list[str]) -> dict:
        """
        Given a user's age, average spend, and cuisines they've already tried,
        return the best wildcard cuisine recommendation from their neighbours.
        """
        if not self.trained:
            raise RuntimeError("Model not trained yet.")

        age_bucket = (age // 5) * 5
        profiles   = self._user_profiles

        # Build the query row for this user
        cuisine_vec = {c: 0.0 for c in self._cuisine_cols}
        for c in tried_cuisines:
            if c in cuisine_vec:
                cuisine_vec[c] = 1.0 / max(len(tried_cuisines), 1)

        query_row = [avg_spend] + [cuisine_vec[c] for c in self._cuisine_cols]
        X_query   = self.scaler.transform([query_row])

        distances, indices = self.model.kneighbors(X_query)

        # Aggregate neighbour preferences
        neighbour_profiles = profiles.iloc[indices[0][1:]]   # exclude self
        neighbour_cuisine_avg = neighbour_profiles[self._cuisine_cols].mean()

        # Find the top cuisine the user hasn't tried
        untried = {c: neighbour_cuisine_avg[c] for c in self._cuisine_cols if c not in tried_cuisines}
        if not untried:
            return {"wildcard": None, "reason": "User has tried all available cuisine types — great explorer!"}

        best_wildcard = max(untried, key=untried.get)
        confidence    = round(untried[best_wildcard] * 100, 1)

        return {
            "wildcard":   best_wildcard,
            "confidence": confidence,
            "message":    f"People with your taste profile are loving {best_wildcard} this week. Want to try something new?",
            "neighbours_checked": self.K,
        }

    def summary(self) -> dict:
        return {
            "model":        "WildcardRecommender",
            "status":       self.status,
            "data_source":  "Kaggle daily_food_delivery_orders.csv",
            "segments":     getattr(self, "train_n", 0),
            "k":            self.K,
            "cuisine_types": CUISINE_TYPES,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Convenience factory
# ─────────────────────────────────────────────────────────────────────────────
def build_and_train():
    """Load data, train both models, return them ready-to-use."""
    df      = _load_data()
    nudge   = LoneBirdTimeNudge()
    wildcard = WildcardRecommender()
    nudge.train(df)
    wildcard.train(df)
    return nudge, wildcard
