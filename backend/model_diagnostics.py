"""
model_diagnostics.py  —  NaanStop Tiffin | Post 6 (Random Forest & XGBoost)
==============================================================================
A full "watch the model learn, then grade it honestly" report.

  PART A  CALIBRATION  — watch train-MAE vs validation-MAE as boosting rounds
                         climb. Early stopping finds the "seen enough" point.
                         The train/val GAP tells us bias vs variance.
  PART B  LEARNING CURVE — would MORE data help? Train on 10/25/50/100% and
                         watch the validation error.
  PART C  HONEST TEST  — score on a physically separate holdout file with
                         PROVEN zero ID overlap. No cheating.
  PART D  ERROR ANALYSIS — where the model is GOOD and where it's LACKING:
                         bias direction, accuracy bands, error per segment
                         (traffic / city / festival / distance / speed), and
                         the worst misses.

Requires the split files written by smoke_test_separated_eval.py
(food_delivery_train_split.csv + food_delivery_holdout_test.csv). If they're
missing this script regenerates them.

Run from the backend/ directory:
  python model_diagnostics.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from ai.delivery_eta_xgboost import (
    DeliveryETAPredictor, _load_data, FEATURE_COLS, CATEGORICAL_COLS,
)

GRN  = "\033[92m"
YLW  = "\033[93m"
RED  = "\033[91m"
CYN  = "\033[96m"
RST  = "\033[0m"
BOLD = "\033[1m"

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
ARCHIVE = os.path.join(_ROOT, "archive")
SOURCE = os.path.join(ARCHIVE, "food_delivery_time_train.csv")
TRAIN_FILE = os.path.join(ARCHIVE, "food_delivery_train_split.csv")
TEST_FILE = os.path.join(ARCHIVE, "food_delivery_holdout_test.csv")


def section(title: str):
    print()
    print(BOLD + "=" * 66 + RST)
    print(BOLD + f"  {title}" + RST)
    print(BOLD + "=" * 66 + RST)


def ensure_split_files():
    if os.path.exists(TRAIN_FILE) and os.path.exists(TEST_FILE):
        return
    full = pd.read_csv(SOURCE)
    test = full.sample(frac=0.2, random_state=42)
    train = full.drop(test.index)
    train.to_csv(TRAIN_FILE, index=False)
    test.to_csv(TEST_FILE, index=False)


def grade(value, good, ok, lower_is_better=True):
    """Colour a metric green/yellow/red against two thresholds."""
    if lower_is_better:
        c = GRN if value <= good else (YLW if value <= ok else RED)
    else:
        c = GRN if value >= good else (YLW if value >= ok else RED)
    return f"{c}{value:.2f}{RST}"


if __name__ == "__main__":
    ensure_split_files()

    # Load the training split and carve an internal validation set from it.
    # The holdout TEST file is NEVER touched until PART C.
    df_train = _load_data(TRAIN_FILE)
    X = df_train[FEATURE_COLS]
    y = df_train["target_minutes"]
    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=7)

    # ── PART A — CALIBRATION (watch it learn) ────────────────────────────────
    section("PART A  CALIBRATION — train-MAE vs validation-MAE per round")
    cal = XGBRegressor(
        n_estimators=800, learning_rate=0.1, max_depth=5,
        subsample=0.8, colsample_bytree=0.8,
        enable_categorical=True, tree_method="hist",
        eval_metric="mae", early_stopping_rounds=30, random_state=42,
    )
    cal.fit(X_tr, y_tr, eval_set=[(X_tr, y_tr), (X_val, y_val)], verbose=False)
    res = cal.evals_result()
    train_curve = res["validation_0"]["mae"]
    val_curve = res["validation_1"]["mae"]
    best = cal.best_iteration

    print(f"  {'round':>6} {'train MAE':>11} {'val MAE':>9} {'gap':>7}")
    milestones = [r for r in [1, 10, 25, 50, 100, 200, 400, best] if r < len(val_curve)]
    for r in sorted(set(milestones)):
        gap = val_curve[r] - train_curve[r]
        tag = f"  {CYN}<- best (early stop){RST}" if r == best else ""
        print(f"  {r:>6} {train_curve[r]:>11.2f} {val_curve[r]:>9.2f} {gap:>7.2f}{tag}")

    final_gap = val_curve[best] - train_curve[best]
    print()
    print(f"  'seen enough' at round  : {best} (of up to 800; rest were wasted)")
    print(f"  train/val gap at best   : {final_gap:.2f} min")
    if final_gap < 0.5:
        print(f"  {GRN}-> tight gap: well-calibrated, not overfitting{RST}")
    elif final_gap < 1.5:
        print(f"  {YLW}-> mild gap: a little variance, acceptable{RST}")
    else:
        print(f"  {RED}-> wide gap: overfitting the training set{RST}")

    # ── PART B — LEARNING CURVE (would more data help?) ──────────────────────
    section("PART B  LEARNING CURVE — does more training data help?")
    print(f"  {'data used':>10} {'rows':>7} {'train MAE':>11} {'val MAE':>9}")
    for frac in [0.10, 0.25, 0.50, 1.0]:
        n = int(len(X_tr) * frac)
        m = XGBRegressor(
            n_estimators=max(best, 100), learning_rate=0.1, max_depth=5,
            subsample=0.8, colsample_bytree=0.8,
            enable_categorical=True, tree_method="hist", random_state=42,
        )
        m.fit(X_tr.iloc[:n], y_tr.iloc[:n])
        tr_mae = mean_absolute_error(y_tr.iloc[:n], m.predict(X_tr.iloc[:n]))
        va_mae = mean_absolute_error(y_val, m.predict(X_val))
        print(f"  {int(frac*100):>9}% {n:>7} {tr_mae:>11.2f} {va_mae:>9.2f}")
    print()
    print("  Read: if val MAE flattens, more data won't help much (low variance);")
    print("        if val MAE is still falling, collecting more data would pay off.")

    # ── PART C — HONEST TEST (no cheating) ───────────────────────────────────
    section("PART C  HONEST TEST — separate holdout file, proven 0 leakage")
    tr_ids = set(pd.read_csv(TRAIN_FILE)["ID"].astype(str).str.strip())
    te_ids = set(pd.read_csv(TEST_FILE)["ID"].astype(str).str.strip())
    print(f"  train/test shared IDs   : {len(tr_ids & te_ids)}  "
          f"({GRN}clean{RST})" if not (tr_ids & te_ids) else
          f"  train/test shared IDs   : {len(tr_ids & te_ids)}  ({RED}LEAKAGE{RST})")

    final = DeliveryETAPredictor(csv_path=TRAIN_FILE, train_full=True)
    df_test = _load_data(TEST_FILE)
    X_test = final._align_categories(df_test[FEATURE_COLS])
    y_test = df_test["target_minutes"].values
    preds = final.model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    bias = float(np.mean(preds - y_test))
    print(f"  rows scored             : {len(y_test)}")
    print(f"  MAE  (avg miss)         : {grade(mae, 3.5, 5.0)} min")
    print(f"  RMSE (punishes big miss): {grade(rmse, 4.5, 6.5)} min")
    print(f"  R2   (variance explained): {grade(r2, 0.80, 0.60, lower_is_better=False)}")
    bias_word = "over-predicts" if bias > 0 else "under-predicts"
    print(f"  mean bias               : {bias:+.2f} min  (model {bias_word} on average)")

    # ── PART D — ERROR ANALYSIS (good vs lacking) ────────────────────────────
    section("PART D  ERROR ANALYSIS — where it's GOOD, where it's LACKING")
    err = pd.DataFrame({
        "actual": y_test,
        "pred": preds,
        "abs_err": np.abs(preds - y_test),
        "signed_err": preds - y_test,
    })
    # bring raw segment columns alongside (reset index to align positionally)
    seg = df_test.reset_index(drop=True)
    err = err.reset_index(drop=True)

    within5 = (err["abs_err"] <= 5).mean() * 100
    within10 = (err["abs_err"] <= 10).mean() * 100
    print(f"  predictions within +-5 min : {within5:5.1f}%")
    print(f"  predictions within +-10 min: {within10:5.1f}%")

    def segment_report(col_values, label, order=None):
        print()
        print(f"  --- error by {label} ---")
        tmp = err.copy()
        tmp["seg"] = col_values.values
        groups = tmp.groupby("seg")
        keys = order if order else sorted(groups.groups.keys())
        for k in keys:
            if k not in groups.groups:
                continue
            g = groups.get_group(k)
            print(f"    {str(k):20s} n={len(g):5d}  MAE={g['abs_err'].mean():5.2f}  "
                  f"bias={g['signed_err'].mean():+5.2f}")

    segment_report(seg["Road_traffic_density"], "road traffic",
                   order=["Low", "Medium", "High", "Jam", "NaN"])
    segment_report(seg["City"], "city",
                   order=["Urban", "Metropolitian", "Semi-Urban", "NaN"])
    segment_report(seg["Festival"], "festival", order=["No", "Yes", "NaN"])

    # by actual delivery speed bucket — models often nail the middle, miss extremes
    speed_bucket = pd.cut(err["actual"], bins=[0, 20, 35, 100],
                          labels=["fast (<20)", "medium (20-35)", "slow (>35)"])
    segment_report(speed_bucket, "actual speed bucket",
                   order=["fast (<20)", "medium (20-35)", "slow (>35)"])

    # by distance bucket
    dist_bucket = pd.cut(seg["distance_km"], bins=[0, 5, 10, 20, 1e6],
                         labels=["<5km", "5-10km", "10-20km", ">20km"])
    segment_report(dist_bucket, "distance bucket",
                   order=["<5km", "5-10km", "10-20km", ">20km"])

    # worst misses
    print()
    print(f"  --- 5 worst misses ---")
    worst = err.sort_values("abs_err", ascending=False).head(5)
    for idx, row in worst.iterrows():
        traffic = seg.loc[idx, "Road_traffic_density"]
        fest = seg.loc[idx, "Festival"]
        print(f"    actual={row['actual']:5.0f}  pred={row['pred']:5.1f}  "
              f"miss={row['signed_err']:+6.1f}   traffic={traffic}, festival={fest}")

    print()
    print(BOLD + "  Diagnostics complete." + RST)
    print()
