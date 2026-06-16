"""
delivery_eta_xgboost.py  —  NaanStop Tiffin | Post 6 (Random Forest & XGBoost)
──────────────────────────────────────────────────────────────────────────────
DeliveryETAPredictor
  Predicts Time_taken(min) for a delivery — the regression follow-up to
  Post 2's DeliveryRiskClassifier ("is this risky?" -> "how many minutes?").

  Algorithm: XGBRegressor (gradient boosting)
    - Each tree is trained on the RESIDUAL of the previous ensemble:
          F_m(x) = F_{m-1}(x) + eta * h_m(x)
      For regression the residual is literally "how many minutes off was
      the last guess" — e.g. predicted 32, actual 38 -> next tree learns +6.

    - subsample=0.8 / colsample_bytree=0.8 (Friedman 2002, Stochastic
      Gradient Boosting): each round trains on a random 80% of rows and
      80% of columns. This bakes Random Forest's bagging idea (reduces
      variance) directly INTO the sequential boosting process (reduces
      bias) — one model doing the job of two ("V2 is the blend").

  Feature: distance_km — same Haversine formula as
    backend/ai/decision_tree.py's _haversine_km, applied to the
    Restaurant -> Delivery coordinates in this dataset.

Data source: archive/food_delivery_time_train.csv (Kaggle, 45,593 rows)
  Kaggle's accompanying test.csv has no Time_taken(min) labels, so
  evaluation uses our own 80/20 split of train.csv.

  Missing-data note: ~4% of rows have no rating/age/traffic reading.
  XGBoost handles missing numeric values natively (learns a default split
  direction) and "NaN" already appears as its own category for
  Weatherconditions/Road_traffic_density/City/Festival — both are kept
  as signal rather than imputed away.
"""

import os
import re

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# ── Path helpers ─────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
DATA_PATH = os.path.join(_ROOT, "archive", "food_delivery_time_train.csv")

# ── Feature config ───────────────────────────────────────────────────────────
NUMERIC_COLS = [
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Vehicle_condition",
    "multiple_deliveries",
    "distance_km",
]

CATEGORICAL_COLS = [
    "Weatherconditions",
    "Road_traffic_density",
    "Type_of_order",
    "Type_of_vehicle",
    "City",
    "Festival",
]

FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS


# ─────────────────────────────────────────────────────────────────────────────
# Haversine — same formula as decision_tree.py's _haversine_km, vectorized
# for ~45k rows via numpy instead of a per-row scalar call.
# ─────────────────────────────────────────────────────────────────────────────
def _haversine_km_series(lat1, lng1, lat2, lng2) -> pd.Series:
    R = 6371.0  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lng2 - lng1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


# ─────────────────────────────────────────────────────────────────────────────
# Data loading + feature engineering
# ─────────────────────────────────────────────────────────────────────────────
def _load_data(csv_path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # "(min) 24" -> 24.0
    df["target_minutes"] = df["Time_taken(min)"].str.extract(r"(\d+)").astype(float)

    df["distance_km"] = _haversine_km_series(
        df["Restaurant_latitude"], df["Restaurant_longitude"],
        df["Delivery_location_latitude"], df["Delivery_location_longitude"],
    )

    for col in ["Delivery_person_Age", "Delivery_person_Ratings", "multiple_deliveries"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors="coerce")

    for col in CATEGORICAL_COLS:
        df[col] = df[col].astype(str).str.strip().astype("category")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# DeliveryETAPredictor
# ─────────────────────────────────────────────────────────────────────────────
class DeliveryETAPredictor:
    def __init__(
        self,
        csv_path: str = DATA_PATH,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        learning_rate: float = 0.1,
        n_estimators: int = 300,
        max_depth: int = 5,
        random_state: int = 42,
        train_full: bool = False,
    ):
        df = _load_data(csv_path)

        X = df[FEATURE_COLS]
        y = df["target_minutes"]

        if train_full:
            # Train on every row — used when a SEPARATE labelled test file will
            # be supplied via evaluate_on_file(). X_test/y_test are left empty.
            self.X_train, self.y_train = X, y
            self.X_test = X.iloc[0:0]
            self.y_test = y.iloc[0:0]
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=0.2, random_state=random_state
            )

        # Remember the exact training categories per column so that a single
        # incoming order can be encoded with IDENTICAL codes at predict time.
        # (If we let pandas re-infer categories from one row, the codes would
        #  silently misalign with training and predictions would be wrong.)
        self.categories_ = {
            col: self.X_train[col].cat.categories for col in CATEGORICAL_COLS
        }

        self.model = XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            enable_categorical=True,
            tree_method="hist",
            random_state=random_state,
        )
        self.model.fit(self.X_train, self.y_train)

    def evaluate(self) -> float:
        """Mean Absolute Error (minutes) on the held-out 20% split."""
        preds = self.model.predict(self.X_test)
        return mean_absolute_error(self.y_test, preds)

    def _align_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Re-cast categorical columns to the EXACT training categories so the
        integer codes XGBoost sees line up with what it learned. Without this,
        an external file's categories could map to different codes silently."""
        df = df.copy()
        for col in CATEGORICAL_COLS:
            df[col] = pd.Categorical(
                df[col].astype(str).str.strip(), categories=self.categories_[col]
            )
        return df

    def evaluate_on_file(self, csv_path: str):
        """
        True out-of-sample test: load a SEPARATE labelled CSV (different rows
        from training), score it, and return (mae, n_rows, sample_df).
        The caller is responsible for ensuring the file shares no IDs with
        the training data — this method asserts nothing about leakage.
        """
        df = _load_data(csv_path)
        X = self._align_categories(df[FEATURE_COLS])
        y = df["target_minutes"]
        preds = self.model.predict(X)
        mae = mean_absolute_error(y, preds)
        sample = pd.DataFrame({
            "actual_min": y.values[:6],
            "predicted_min": np.round(preds[:6], 1),
        })
        return mae, len(df), sample

    def feature_importances(self) -> list[tuple[str, float]]:
        return sorted(
            zip(FEATURE_COLS, self.model.feature_importances_),
            key=lambda pair: -pair[1],
        )

    def sample_predictions(self, n: int = 5) -> pd.DataFrame:
        """A few (actual, predicted) ETA pairs from the test split, for smoke-test output."""
        sample_X = self.X_test.iloc[:n]
        sample_y = self.y_test.iloc[:n]
        preds = self.model.predict(sample_X)
        return pd.DataFrame({
            "actual_min": sample_y.values,
            "predicted_min": np.round(preds, 1),
        })

    def predict_one(self, **features) -> float:
        """
        The real production call: predict the ETA (minutes) for ONE new order.

        Pass any subset of FEATURE_COLS as keyword args; missing ones become
        NaN, which XGBoost handles natively. Categorical values are encoded
        against the stored training categories so codes line up exactly.

        Example:
            eta = model.predict_one(
                Delivery_person_Age=30, Delivery_person_Ratings=4.5,
                Vehicle_condition=1, multiple_deliveries=2, distance_km=5.0,
                Road_traffic_density="Jam", Weatherconditions="conditions Fog",
                Type_of_order="Meal", Type_of_vehicle="motorcycle",
                City="Metropolitian", Festival="No",
            )
        """
        row = {col: features.get(col, np.nan) for col in FEATURE_COLS}
        df = pd.DataFrame([row])
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in CATEGORICAL_COLS:
            value = str(df[col].iloc[0]).strip()
            df[col] = pd.Categorical([value], categories=self.categories_[col])
        df = df[FEATURE_COLS]
        return float(self.model.predict(df)[0])


# ─────────────────────────────────────────────────────────────────────────────
# Ordinal-encoded splits — for fair head-to-head comparisons against models that
# (unlike XGBoost) can't consume pandas category dtype directly, e.g. sklearn's
# RandomForestRegressor. Tree models treat the integer codes as ordinal splits.
# ─────────────────────────────────────────────────────────────────────────────
def encoded_splits(predictor: "DeliveryETAPredictor"):
    def _enc(X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        for col in CATEGORICAL_COLS:
            X[col] = X[col].cat.codes
        return X

    return (
        _enc(predictor.X_train),
        _enc(predictor.X_test),
        predictor.y_train,
        predictor.y_test,
    )
