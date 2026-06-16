"""
demand_forecast.py  —  NaanStop Tiffin | Post 6 (Random Forest & XGBoost)
==============================================================================
DemandForecaster — "14 people in your town are looking for food right now."

The cook-side counterpart to the delivery-ETA model. Same gradient-boosting
engine, different objective:

    ETA model     : XGBRegressor(objective="reg:squarederror")   -> minutes
    Demand model  : XGBRegressor(objective="count:poisson")      -> # of lookers

Counts are non-negative integers, so Poisson is the statistically correct
objective (squared-error would predict negative demand and over-weight busy
cells).

── The cold-start problem ───────────────────────────────────────────────────
There is no public dataset that targets *tiffin* demand (generic food-delivery
sets have no notion of "daily tiffin eater" or "tied to another tiffin"). So,
exactly like Post 3's Surplus Matcher, we bootstrap from synthetic data built
on real-world logical rules, to be replaced by live pilot data later.

── The grain ────────────────────────────────────────────────────────────────
One row = one (area x day x meal_slot x cuisine) cell. Target = how many people
were looking for that cuisine, in that area, in that meal slot, that day.

── The demand rule encoded (the model should re-discover it) ─────────────────
Four user segments, with different propensity to actually order:

    lone_bird    daily tiffin eater, uncommitted   -> 0.70  (addressable)
    other_tiffin  tied to a DIFFERENT tiffin         -> 0.60  (winnable)
    inapp_cook    already subscribed to THIS cook     -> 0.20  (already served)
    surfer        just browsing                       -> 0.10  (noise)

Region (the "middle path"):
    India  -> cuisine is state-bound (a Gujarat area mostly wants Gujarati)
    Canada -> multicultural town, cuisines spread fairly evenly
"""

import itertools

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

SEED = 42

# ── Segment order-propensity weights (the rule the model should re-discover) ──
PROPENSITY = {
    "lone_bird": 0.70,
    "other_tiffin": 0.60,
    "inapp_cook": 0.20,
    "surfer": 0.10,
}

CUISINES = ["Gujarati", "Punjabi", "SouthIndian", "Bengali",
            "Maharashtrian", "Continental"]

# India: state -> its dominant cuisine (strong region x cuisine interaction)
INDIA_STATES = {
    "Gujarat": "Gujarati",
    "Punjab": "Punjabi",
    "TamilNadu": "SouthIndian",
    "WestBengal": "Bengali",
    "Maharashtra": "Maharashtrian",
}
CANADA_TOWNS = ["Barrie", "Waterloo", "Mississauga"]  # multicultural mix

MEAL_SLOTS = {"breakfast": 0.5, "lunch": 1.0, "dinner": 0.7}  # slot demand factor
DEMAND_SCALE = 0.15  # tunes absolute looker counts into a sensible range

# ── Feature config ───────────────────────────────────────────────────────────
NUMERIC_COLS = [
    "day_of_week", "is_weekend", "is_holiday",
    "n_lone_birds", "n_other_tiffin", "n_inapp_cook", "n_surfers",
    "cuisine_match_score", "lag_yesterday", "lag_lastweek",
]
CATEGORICAL_COLS = ["country", "region", "area_id", "cuisine_type", "meal_slot"]
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS

TARGETS = ["total_lookers", "addressable_lookers"]


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic data generation (vectorized)
# ─────────────────────────────────────────────────────────────────────────────
def _build_areas(rng: np.random.Generator) -> pd.DataFrame:
    """Two areas per India-state and per Canada-town, each with a population
    split across the four user segments."""
    rows = []
    for state, cuisine in INDIA_STATES.items():
        for a in range(2):
            rows.append({
                "country": "India", "region": state,
                "area_id": f"IN-{state[:3].upper()}-{a+1}",
                "state_cuisine": cuisine,
            })
    for town in CANADA_TOWNS:
        for a in range(2):
            rows.append({
                "country": "Canada", "region": town,
                "area_id": f"CA-{town[:3].upper()}-{a+1}",
                "state_cuisine": None,  # multicultural
            })
    df = pd.DataFrame(rows)
    # segment populations per area — wide swings so the SEGMENT MIX is the
    # dominant demand driver (per the encoded rule), not the region alone.
    df["n_lone_birds"] = rng.integers(10, 90, len(df))
    df["n_other_tiffin"] = rng.integers(20, 130, len(df))  # winnable market, widest swing
    df["n_inapp_cook"] = rng.integers(5, 40, len(df))
    df["n_surfers"] = rng.integers(30, 120, len(df))
    return df


def build_demand_dataset(n_days: int = 120, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    areas = _build_areas(rng)

    # day calendar
    days = pd.DataFrame({"day_index": np.arange(n_days)})
    days["day_of_week"] = days["day_index"] % 7
    days["is_weekend"] = (days["day_of_week"] >= 5).astype(int)
    days["is_holiday"] = (rng.random(n_days) < 0.05).astype(int)

    # cross join area x day x slot x cuisine
    grid = pd.DataFrame(
        itertools.product(areas["area_id"], days["day_index"],
                          MEAL_SLOTS.keys(), CUISINES),
        columns=["area_id", "day_index", "meal_slot", "cuisine_type"],
    )
    grid = grid.merge(areas, on="area_id").merge(days, on="day_index")

    # cuisine_match_score
    india = grid["country"].eq("India")
    # Region still matters, but with a gentler swing so it does not swamp the
    # segment mix: India non-matching cuisine is dampened (0.5) not killed (0.15).
    match = np.where(
        india,
        np.where(grid["cuisine_type"] == grid["state_cuisine"], 1.0, 0.5),
        0.75,  # Canada: diverse, fairly even across cuisines
    )
    # small deterministic per-(area,cuisine) wobble so Canada isn't perfectly flat
    wobble = (pd.util.hash_pandas_object(
        grid["area_id"].astype(str) + grid["cuisine_type"].astype(str),
        index=False).to_numpy() % 100) / 100.0  # 0..1
    match = match + np.where(india, 0.0, (wobble - 0.5) * 0.2)
    grid["cuisine_match_score"] = match.clip(0.3, 1.0)

    # demand factors
    slot_factor = grid["meal_slot"].map(MEAL_SLOTS).to_numpy()
    day_factor = np.where(grid["is_weekend"].to_numpy() == 1, 0.6, 1.0)  # tiffin = office crowd
    holiday_factor = np.where(grid["is_holiday"].to_numpy() == 1, 0.5, 1.0)

    # demand potential from the segment mix (the encoded rule)
    potential = (
        grid["n_lone_birds"] * PROPENSITY["lone_bird"]
        + grid["n_other_tiffin"] * PROPENSITY["other_tiffin"]
        + grid["n_inapp_cook"] * PROPENSITY["inapp_cook"]
        + grid["n_surfers"] * PROPENSITY["surfer"]
    ).to_numpy()

    expected_total = (potential * grid["cuisine_match_score"].to_numpy()
                      * slot_factor * day_factor * holiday_factor * DEMAND_SCALE)
    grid["total_lookers"] = rng.poisson(np.clip(expected_total, 0, None))

    # addressable share = lone_bird + other_tiffin contribution (factors cancel)
    addr_potential = (grid["n_lone_birds"] * PROPENSITY["lone_bird"]
                      + grid["n_other_tiffin"] * PROPENSITY["other_tiffin"]).to_numpy()
    p_addr = np.clip(addr_potential / np.clip(potential, 1e-9, None), 0, 1)
    grid["addressable_lookers"] = rng.binomial(grid["total_lookers"].to_numpy(), p_addr)

    # lag features (per area/slot/cuisine time series)
    grid = grid.sort_values(["area_id", "meal_slot", "cuisine_type", "day_index"])
    g = grid.groupby(["area_id", "meal_slot", "cuisine_type"])["total_lookers"]
    grid["lag_yesterday"] = g.shift(1)
    grid["lag_lastweek"] = g.shift(7)

    return grid.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# DemandForecaster
# ─────────────────────────────────────────────────────────────────────────────
class DemandForecaster:
    def __init__(
        self,
        target: str = "total_lookers",
        n_days: int = 120,
        n_estimators: int = 300,
        learning_rate: float = 0.1,
        max_depth: int = 5,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = SEED,
    ):
        assert target in TARGETS, f"target must be one of {TARGETS}"
        self.target = target
        self.df = build_demand_dataset(n_days=n_days, seed=random_state)

        for col in CATEGORICAL_COLS:
            self.df[col] = self.df[col].astype("category")

        X = self.df[FEATURE_COLS]
        y = self.df[target]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        self.categories_ = {c: self.X_train[c].cat.categories for c in CATEGORICAL_COLS}

        self.model = XGBRegressor(
            objective="count:poisson",
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
        return mean_absolute_error(self.y_test, self.model.predict(self.X_test))

    def feature_importances(self):
        return sorted(zip(FEATURE_COLS, self.model.feature_importances_),
                      key=lambda p: -p[1])

    def predict_row(self, row: pd.Series) -> float:
        """Predict expected lookers for a single grid row (Series of features)."""
        df = pd.DataFrame([row[FEATURE_COLS]])
        for col in CATEGORICAL_COLS:
            df[col] = pd.Categorical([str(row[col])], categories=self.categories_[col])
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return float(self.model.predict(df[FEATURE_COLS])[0])


# ── Encoded splits for fair RandomForest comparison (RF can't take category) ──
def encoded_splits(forecaster: "DemandForecaster"):
    def _enc(X):
        X = X.copy()
        for c in CATEGORICAL_COLS:
            X[c] = X[c].cat.codes
        return X
    return (_enc(forecaster.X_train), _enc(forecaster.X_test),
            forecaster.y_train, forecaster.y_test)
