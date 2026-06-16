"""
smoke_test_separated_eval.py  —  NaanStop Tiffin | Post 6
==============================================================================
TRUE train/test separation across PHYSICALLY SEPARATE files.

The Kaggle archive ships train.csv (labelled) and test.csv (labels removed),
so test.csv can't be scored. To get a real, leakage-free error number we split
the labelled data ourselves into two files with ZERO overlapping order IDs:

    archive/food_delivery_train_split.csv   (80%, model trains on this)
    archive/food_delivery_holdout_test.csv  (20%, model has NEVER seen this)

Then we train on the first file and score on the second — and prove the two
share no IDs, so there is no possibility of leakage.

Run from the backend/ directory:
  python smoke_test_separated_eval.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd

from ai.delivery_eta_xgboost import DeliveryETAPredictor

GRN  = "\033[92m"
YLW  = "\033[93m"
RED  = "\033[91m"
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
    print(BOLD + "=" * 64 + RST)
    print(BOLD + f"  {title}" + RST)
    print(BOLD + "=" * 64 + RST)


if __name__ == "__main__":
    # ── STEP 1 — split the labelled data into two separate files ─────────────
    section("STEP 1  Split labelled data into two separate files")
    full = pd.read_csv(SOURCE)
    test = full.sample(frac=0.2, random_state=42)
    train = full.drop(test.index)
    train.to_csv(TRAIN_FILE, index=False)
    test.to_csv(TEST_FILE, index=False)
    print(f"  source rows        : {len(full)}")
    print(f"  -> train_split.csv : {len(train)} rows")
    print(f"  -> holdout_test.csv: {len(test)} rows")

    # ── STEP 2 — PROVE the two files share no order IDs ──────────────────────
    section("STEP 2  Prove zero leakage (no shared order IDs)")
    train_ids = set(train["ID"].astype(str).str.strip())
    test_ids = set(test["ID"].astype(str).str.strip())
    overlap = train_ids & test_ids
    print(f"  train IDs          : {len(train_ids)}")
    print(f"  test IDs           : {len(test_ids)}")
    if overlap:
        print(f"  {RED}ID overlap         : {len(overlap)}  <-- LEAKAGE!{RST}")
    else:
        print(f"  {GRN}ID overlap         : 0  -> clean separation{RST}")

    # ── STEP 3 — train ONLY on the train file ────────────────────────────────
    section("STEP 3  Train on train_split.csv only (train_full=True)")
    model = DeliveryETAPredictor(csv_path=TRAIN_FILE, train_full=True)
    print(f"  rows trained on    : {len(model.X_train)}")
    print(f"  rows model can see : 0 from the holdout file")

    # ── STEP 4 — score on the never-seen holdout file ────────────────────────
    section("STEP 4  Score on holdout_test.csv (truly unseen rows)")
    mae, n, sample = model.evaluate_on_file(TEST_FILE)
    print(f"  rows scored        : {n}")
    print(f"  {GRN}MAE (minutes)      : {mae:.2f}{RST}")
    print()
    print("  sample (actual -> predicted):")
    for _, row in sample.iterrows():
        a, p = row["actual_min"], row["predicted_min"]
        diff = p - a
        col = GRN if abs(diff) <= 5 else YLW
        print(f"    {a:5.0f} -> {p:5.1f}   {col}({diff:+5.1f}){RST}")

    print()
    print(BOLD + "  Separated-file evaluation complete." + RST)
    print(f"  Compare to the in-memory 80/20 split MAE (3.15) from")
    print(f"  smoke_test_xgboost_eta.py — they should land in the same ballpark,")
    print(f"  confirming the original number was not inflated by leakage.")
    print()
