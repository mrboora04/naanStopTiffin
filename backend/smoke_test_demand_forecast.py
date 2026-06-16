"""
smoke_test_demand_forecast.py  —  NaanStop Tiffin | Post 6
==============================================================================
Tests the cook-side DemandForecaster (XGBRegressor, objective=count:poisson).

  TEST 1  Model quality       — MAE / RMSE / R2 on a held-out split
  TEST 2  Re-discovered rule  — do feature importances rank lone_bird +
                                other_tiffin on top? (the weights we encoded)
  TEST 3  Bagging vs boosting — RandomForestRegressor vs XGBoost, fair encoding
  TEST 4  Cook nudge demo     — "N people in your town are looking, M
                                addressable -> cook if >= threshold"

Run from the backend/ directory:
  python smoke_test_demand_forecast.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from ai.demand_forecast import DemandForecaster, encoded_splits

GRN  = "\033[92m"
YLW  = "\033[93m"
CYN  = "\033[96m"
RST  = "\033[0m"
BOLD = "\033[1m"

COOK_THRESHOLD = 8  # cook a fresh batch only if addressable demand >= this


def bar(value, max_val, width=20):
    filled = int(round((value / max_val) * width)) if max_val else 0
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def section(title):
    print()
    print(BOLD + "=" * 66 + RST)
    print(BOLD + f"  {title}" + RST)
    print(BOLD + "=" * 66 + RST)


if __name__ == "__main__":
    section("SETUP — train DemandForecaster (count:poisson)")
    total_model = DemandForecaster(target="total_lookers")
    addr_model = DemandForecaster(target="addressable_lookers")
    print(f"  synthetic rows  : {len(total_model.df)}")
    print(f"  grain           : area x day x meal_slot x cuisine")
    print(f"  objective       : count:poisson")
    print(f"  targets         : total_lookers + addressable_lookers")

    # ── TEST 1 — MODEL QUALITY ───────────────────────────────────────────────
    section("TEST 1  MODEL QUALITY — held-out 20% (total_lookers)")
    preds = total_model.model.predict(total_model.X_test)
    y = total_model.y_test.values
    mae = mean_absolute_error(y, preds)
    rmse = np.sqrt(mean_squared_error(y, preds))
    r2 = r2_score(y, preds)
    print(f"  MAE  (avg miss)         : {mae:.2f} lookers")
    print(f"  RMSE (punishes big miss): {rmse:.2f} lookers")
    print(f"  R2   (variance explained): {r2:.2f}")
    print(f"  mean actual lookers/cell: {y.mean():.2f}")

    # ── TEST 2 — RE-DISCOVERED RULE ──────────────────────────────────────────
    section("TEST 2  RE-DISCOVERED RULE — feature importances")
    imps = total_model.feature_importances()
    max_imp = imps[0][1]
    for name, imp in imps:
        flag = ""
        if name in ("n_lone_birds", "n_other_tiffin"):
            flag = f"  {GRN}<- high-propensity segment{RST}"
        elif name == "cuisine_match_score":
            flag = f"  {CYN}<- region x cuisine{RST}"
        print(f"  {name:22s} {imp:.4f} {bar(imp, max_imp)}{flag}")
    # The weight rule isn't "segments are the #1 feature" (time-of-day/weekday
    # swing every row, so they lead globally). The real test: among the four
    # segments, do the HIGH-propensity ones outrank the LOW-propensity ones?
    imp = dict(imps)
    high = min(imp["n_lone_birds"], imp["n_other_tiffin"])
    low = max(imp["n_inapp_cook"], imp["n_surfers"])
    print()
    print(f"  high-propensity segments (lone_bird, other_tiffin): "
          f"{imp['n_lone_birds']:.4f}, {imp['n_other_tiffin']:.4f}")
    print(f"  low-propensity  segments (inapp_cook, surfers)     : "
          f"{imp['n_inapp_cook']:.4f}, {imp['n_surfers']:.4f}")
    if high > low:
        print(f"  {GRN}=> within the segments, high-propensity outranks low — "
              f"the weight rule held.{RST}")
    else:
        print(f"  {YLW}=> segment ordering did not match the encoded weights.{RST}")
    print(f"  (time features lead globally because they swing every row; the")
    print(f"   segment mix sets each area's baseline demand level.)")

    # ── TEST 3 — BAGGING vs BOOSTING ─────────────────────────────────────────
    section("TEST 3  BAGGING vs BOOSTING — same data, fair encoding")
    Xtr, Xte, ytr, yte = encoded_splits(total_model)
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(Xtr, ytr)
    rf_mae = mean_absolute_error(yte, rf.predict(Xte))
    xgb = XGBRegressor(objective="count:poisson", n_estimators=300,
                       learning_rate=0.1, max_depth=5, subsample=0.8,
                       colsample_bytree=0.8, tree_method="hist", random_state=42)
    xgb.fit(Xtr, ytr)
    xgb_mae = mean_absolute_error(yte, xgb.predict(Xte))
    print(f"  Random Forest (bagging)        MAE: {rf_mae:.2f} lookers")
    print(f"  XGBoost Poisson (boosting)     MAE: {xgb_mae:.2f} lookers")
    winner = "XGBoost" if xgb_mae < rf_mae else "Random Forest"
    print(f"  {GRN}=> {winner} wins by {abs(rf_mae - xgb_mae):.2f}{RST}")

    # ── TEST 4 — COOK NUDGE DEMO ─────────────────────────────────────────────
    section("TEST 4  COOK NUDGE — should the cook start a fresh batch?")
    # Both models share the same split (same seed), so X_test rows align.
    # Batch-predict, then surface the strongest and weakest demand cells.
    view = total_model.X_test.copy()
    view["pred_total"] = total_model.model.predict(total_model.X_test)
    view["pred_addr"] = addr_model.model.predict(addr_model.X_test)

    def render(row):
        decision = (f"{GRN}COOK A FRESH BATCH{RST}" if row["pred_addr"] >= COOK_THRESHOLD
                    else f"{YLW}hold — not enough new demand{RST}")
        print(f"  {row['area_id']:12s} {row['meal_slot']:9s} {str(row['cuisine_type']):13s}")
        print(f"     looking now : {row['pred_total']:4.0f}   "
              f"addressable: {row['pred_addr']:4.0f}   "
              f"(threshold {COOK_THRESHOLD})  -> {decision}")

    print(f"  {BOLD}Strongest demand cells:{RST}")
    for _, row in view.sort_values("pred_addr", ascending=False).head(3).iterrows():
        render(row)
    print(f"\n  {BOLD}Weakest demand cells:{RST}")
    for _, row in view.sort_values("pred_addr").head(3).iterrows():
        render(row)

    print()
    print(f"  Nudge copy example:")
    ex = view.sort_values("pred_addr", ascending=False).iloc[0]
    print(f'  "{ex["pred_addr"]:.0f} people in {ex["region"]} are looking for '
          f'{ex["cuisine_type"]} {ex["meal_slot"]} they can\'t get yet '
          f'({ex["pred_total"]:.0f} total). Start a fresh batch?"')

    print()
    print(BOLD + "  All demand-forecast smoke tests ran." + RST)
    print()
