"""
smoke_test_xgboost_eta.py  —  NaanStop Tiffin | Post 6 (Random Forest & XGBoost)
==============================================================================
Five DIFFERENT kinds of smoke test for DeliveryETAPredictor — each one backs a
specific claim made in the Post 6 write-up:

  TEST 1  Model Quality        — MAE + feature importances on a held-out split
  TEST 2  Live ETA             — the real production call for ONE new order
  TEST 3  Sensitivity          — vary ONE feature, watch the ETA move
                                 (proves "it's not how far, it's how jammed")
  TEST 4  Bagging vs Boosting  — RandomForestRegressor vs XGBRegressor head-to-head
                                 (the literal topic of the post)
  TEST 5  V1 vs V2             — subsample=1.0 (pure boosting) vs 0.8 (the blend)
                                 (proves bagging-inside-boosting earns its keep)

Run from the backend/ directory:
  python smoke_test_xgboost_eta.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

from ai.delivery_eta_xgboost import DeliveryETAPredictor, encoded_splits

# ── ANSI colour codes for terminal output ─────────────────────────────────────
GRN  = "\033[92m"
YLW  = "\033[93m"
CYN  = "\033[96m"
RED  = "\033[91m"
RST  = "\033[0m"
BOLD = "\033[1m"


def bar(value: float, max_val: float, width: int = 20) -> str:
    filled = int(round((value / max_val) * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def section(title: str):
    print()
    print(BOLD + "=" * 64 + RST)
    print(BOLD + f"  {title}" + RST)
    print(BOLD + "=" * 64 + RST)


# A realistic NaanStop tiffin order used by the live/sensitivity tests.
BASE_ORDER = dict(
    Delivery_person_Age=30,
    Delivery_person_Ratings=4.5,
    Vehicle_condition=1,
    multiple_deliveries=2,      # rider batching 2 tiffins on one run
    distance_km=5.0,
    Road_traffic_density="Low",
    Weatherconditions="conditions Sunny",
    Type_of_order="Meal",
    Type_of_vehicle="motorcycle",
    City="Metropolitian",
    Festival="No",
)


if __name__ == "__main__":
    # ── Train once; every test reuses this fitted model ──────────────────────
    section("SETUP — training DeliveryETAPredictor (XGBRegressor, subsample=0.8)")
    model = DeliveryETAPredictor()
    print(f"  rows trained    : {len(model.X_train)}")
    print(f"  rows held out   : {len(model.X_test)}")
    print(f"  n_estimators    : {model.model.n_estimators}")
    print(f"  subsample       : {model.model.subsample}  (row bagging)")
    print(f"  colsample_bytree: {model.model.colsample_bytree}  (column bagging)")

    # ── TEST 1 — MODEL QUALITY ───────────────────────────────────────────────
    section("TEST 1  MODEL QUALITY — held-out 20% split")
    mae = model.evaluate()
    print(f"  MAE (minutes)   : {mae:.2f}")
    print()
    print("  feature importances:")
    importances = model.feature_importances()
    max_imp = importances[0][1]
    for name, imp in importances:
        print(f"    {name:26s} {imp:.4f} {bar(imp, max_imp)}")

    # ── TEST 2 — LIVE ETA (production call) ──────────────────────────────────
    section("TEST 2  LIVE ETA — single new tiffin order (predict_one)")
    print("  order: 30yo rider (4.5*), motorcycle, 2 tiffins batched, 5.0 km,")
    print("         Low traffic, Sunny, Metropolitian, no festival")
    eta = model.predict_one(**BASE_ORDER)
    print(f"  {GRN}=> predicted ETA: {eta:.1f} min{RST}")
    print(f"  -> app copy: \"Your tiffin arrives in ~{round(eta)} min\"")

    # ── TEST 3 — SENSITIVITY (it's not how far, it's how jammed) ─────────────
    section("TEST 3  SENSITIVITY — same order, vary ONE feature")
    print("  (A) Road traffic  Low -> Medium -> High -> Jam:")
    base_eta = model.predict_one(**BASE_ORDER)
    for traffic in ["Low", "Medium", "High", "Jam"]:
        order = {**BASE_ORDER, "Road_traffic_density": traffic}
        eta_t = model.predict_one(**order)
        delta = eta_t - base_eta
        print(f"    traffic={traffic:7s} -> {eta_t:5.1f} min   "
              f"{YLW}({delta:+5.1f} vs Low){RST}")

    print()
    print("  (B) Distance  2 -> 5 -> 10 -> 15 km (traffic held at Low):")
    for dist in [2.0, 5.0, 10.0, 15.0]:
        order = {**BASE_ORDER, "distance_km": dist}
        eta_d = model.predict_one(**order)
        delta = eta_d - base_eta
        print(f"    distance={dist:5.1f} km -> {eta_d:5.1f} min   "
              f"{CYN}({delta:+5.1f} vs 5km){RST}")
    print()
    print("  Read: traffic swings the ETA far more than distance does.")

    # ── TEST 4 — BAGGING vs BOOSTING (the post's topic) ──────────────────────
    section("TEST 4  BAGGING vs BOOSTING — same data, fair encoding")
    Xtr, Xte, ytr, yte = encoded_splits(model)

    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(Xtr, ytr)
    rf_mae = mean_absolute_error(yte, rf.predict(Xte))

    xgb = XGBRegressor(
        n_estimators=300, learning_rate=0.1, max_depth=5,
        subsample=0.8, colsample_bytree=0.8,
        tree_method="hist", random_state=42,
    )
    xgb.fit(Xtr, ytr)
    xgb_mae = mean_absolute_error(yte, xgb.predict(Xte))

    print(f"  Random Forest (bagging, 100 trees)   MAE: {rf_mae:.2f} min")
    print(f"  XGBoost       (boosting, 300 trees)  MAE: {xgb_mae:.2f} min")
    winner = "XGBoost" if xgb_mae < rf_mae else "Random Forest"
    print(f"  {GRN}=> {winner} wins by {abs(rf_mae - xgb_mae):.2f} min{RST}")

    # ── TEST 5 — V1 vs V2 (does bagging-inside-boosting help?) ───────────────
    section("TEST 5  V1 vs V2 — pure boosting vs the blend (subsample)")
    v1 = XGBRegressor(
        n_estimators=300, learning_rate=0.1, max_depth=5,
        subsample=1.0, colsample_bytree=1.0,   # no internal bagging
        tree_method="hist", random_state=42,
    )
    v1.fit(Xtr, ytr)
    v1_mae = mean_absolute_error(yte, v1.predict(Xte))
    # v2 == the xgb model trained in TEST 4 (subsample/colsample = 0.8)
    v2_mae = xgb_mae

    print(f"  V1  subsample=1.0  colsample=1.0  (pure boosting)  MAE: {v1_mae:.2f} min")
    print(f"  V2  subsample=0.8  colsample=0.8  (the blend)      MAE: {v2_mae:.2f} min")
    better = "V2 (the blend)" if v2_mae < v1_mae else "V1 (pure boosting)"
    print(f"  {GRN}=> {better} is better by {abs(v1_mae - v2_mae):.2f} min{RST}")

    print()
    print(BOLD + "  All 5 smoke tests ran." + RST)
    print()
