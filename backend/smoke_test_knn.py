"""
smoke_test_knn.py  —  NaanStop Tiffin | KNN Lone Bird Predictor
==============================================================================
Full end-to-end test of both KNN models using the Kaggle dataset.

Simulates:
  - 6 realistic Lone Bird users (different ages, budgets, cuisines tried)
  - Clock at 11:50 AM (20 mins past the predicted 11:30 AM window)
  - Weekly wildcard recommendation run

Run from the backend/ directory:
  python smoke_test_knn.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai.knn import build_and_train, _load_data

# ── ANSI colour codes for terminal output ─────────────────────────────────────
GRN  = "\033[92m"
YLW  = "\033[93m"
CYN  = "\033[96m"
RED  = "\033[91m"
RST  = "\033[0m"
BOLD = "\033[1m"

def bar(value: float, max_val: float = 100, width: int = 20) -> str:
    filled = int(round((value / max_val) * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def section(title: str):
    print()
    print(BOLD + "=" * 60 + RST)
    print(BOLD + f"  {title}" + RST)
    print(BOLD + "=" * 60 + RST)


# ── Synthetic Lone Bird users ─────────────────────────────────────────────────
# In production these come from the DB. For the demo we define them inline.
LONE_BIRDS = [
    {
        "id":               "LB-001",
        "name":             "Arjun (Student, 22)",
        "age":              22,
        "avg_spend":        250.0,
        "avg_distance_km":  3.5,
        "day_of_week":      1,      # Tuesday
        "current_time_min": 710,    # 11:50 AM in minutes since midnight
        "has_ordered_today": False,
        "last_nudge_date":  None,
        "tried_cuisines":   ["Indian"],
    },
    {
        "id":               "LB-002",
        "name":             "Priya (Professional, 34)",
        "age":              34,
        "avg_spend":        650.0,
        "avg_distance_km":  6.1,
        "day_of_week":      1,
        "current_time_min": 710,
        "has_ordered_today": False,
        "last_nudge_date":  None,
        "tried_cuisines":   ["Indian", "Cafe"],
    },
    {
        "id":               "LB-003",
        "name":             "Sam (Already ordered, 29)",
        "age":              29,
        "avg_spend":        400.0,
        "avg_distance_km":  4.0,
        "day_of_week":      1,
        "current_time_min": 710,
        "has_ordered_today": True,   # Should NOT receive nudge
        "last_nudge_date":  None,
        "tried_cuisines":   ["Fast Food", "Chinese"],
    },
    {
        "id":               "LB-004",
        "name":             "Meera (Budget hunter, 45)",
        "age":              45,
        "avg_spend":        320.0,
        "avg_distance_km":  2.8,
        "day_of_week":      1,
        "current_time_min": 710,
        "has_ordered_today": False,
        "last_nudge_date":  None,
        "tried_cuisines":   ["Indian", "Chinese", "Bakery"],
    },
    {
        "id":               "LB-005",
        "name":             "Raj (High spender, 55)",
        "age":              55,
        "avg_spend":        950.0,
        "avg_distance_km":  8.5,
        "day_of_week":      1,
        "current_time_min": 600,    # 10:00 AM — too early for nudge
        "has_ordered_today": False,
        "last_nudge_date":  None,
        "tried_cuisines":   ["Italian", "Cafe"],
    },
    {
        "id":               "LB-006",
        "name":             "Nisha (Explorer, 27)",
        "age":              27,
        "avg_spend":        500.0,
        "avg_distance_km":  5.0,
        "day_of_week":      1,
        "current_time_min": 710,
        "has_ordered_today": False,
        "last_nudge_date":  None,
        "tried_cuisines":   ["Indian", "Chinese", "Italian", "Cafe", "Fast Food", "Bakery"],
    },
]


def main():
    # ── Load & Train ──────────────────────────────────────────────────────────
    section("LOADING KAGGLE DATASET")
    df_raw = _load_data()
    print(f"  Total delivered orders loaded : {len(df_raw)}")
    print(f"  Date range                    : {df_raw['order_date'].min().date()} -> {df_raw['order_date'].max().date()}")
    print(f"  Restaurant types              : {sorted(df_raw['restaurant_type'].unique())}")

    section("TRAINING KNN MODELS")
    nudge_model, wildcard_model = build_and_train()

    ns = nudge_model.summary()
    ws = wildcard_model.summary()

    print(f"\n  [Model 1] {ns['model']}")
    print(f"    status         : {ns['status']}")
    print(f"    rows trained   : {ns['rows_trained']}")
    print(f"    K              : {ns['k']}")
    print(f"    MAE (minutes)  : {ns['mae_minutes']}")

    print(f"\n  [Model 2] {ws['model']}")
    print(f"    status         : {ws['status']}")
    print(f"    user segments  : {ws['segments']}")
    print(f"    K neighbours   : {ws['k']}")

    # ── MODEL 1: Time-Based Nudge ─────────────────────────────────────────────
    section("MODEL 1 — TIME-BASED NUDGE (11:50 AM run)")
    print(f"  Nudge delay threshold : {nudge_model.NUDGE_DELAY_MINUTES} minutes past predicted window\n")

    nudge_count = 0
    for user in LONE_BIRDS:
        result = nudge_model.should_nudge(
            user_id              = user["id"],
            day_of_week          = user["day_of_week"],
            avg_order_value      = user["avg_spend"],
            avg_distance_km      = user["avg_distance_km"],
            minutes_since_midnight = user["current_time_min"],
            has_ordered_today    = user["has_ordered_today"],
            last_nudge_date      = user["last_nudge_date"],
        )

        time_str = f"{user['current_time_min'] // 60:02d}:{user['current_time_min'] % 60:02d}"
        if result["nudge"]:
            nudge_count += 1
            print(f"  {GRN}[SEND NUDGE]{RST}  {user['name']}  (current time: {time_str})")
            print(f"               -> \"{result['message']}\"")
            print(f"               -> Predicted window: {result['predicted_window']} min | Threshold: {result['threshold']} min")
        else:
            print(f"  {YLW}[SKIP]      {RST}  {user['name']}  -> {result['reason']}")
        print()

    print(f"  Nudges queued: {nudge_count} / {len(LONE_BIRDS)} users")

    # ── MODEL 2: Wildcard Recommender ─────────────────────────────────────────
    section("MODEL 2 — WILDCARD RECOMMENDER (weekly run)")
    print("  Finding what your neighbours are eating this week...\n")

    for user in LONE_BIRDS:
        result = wildcard_model.recommend_wildcard(
            age           = user["age"],
            avg_spend     = user["avg_spend"],
            tried_cuisines = user["tried_cuisines"],
        )

        tried_str = ", ".join(user["tried_cuisines"])
        if result["wildcard"]:
            conf = result["confidence"]
            print(f"  {CYN}[WILDCARD]{RST}  {user['name']}")
            print(f"              tried       : {tried_str}")
            print(f"              suggest     : {result['wildcard']}  {bar(conf)} {conf}% neighbour match")
            print(f"              message     : \"{result['message']}\"")
        else:
            print(f"  {YLW}[SKIP]{RST}      {user['name']}  -> {result['reason']}")
        print()

    # ── Feature Importance Proxy ──────────────────────────────────────────────
    section("DATASET INSIGHTS (Bias-Variance Scan)")
    cuisine_counts = df_raw["restaurant_type"].value_counts()
    print("  Order distribution by cuisine type:\n")
    for cuisine, count in cuisine_counts.items():
        pct = count / len(df_raw) * 100
        print(f"    {cuisine:<12} {bar(pct, 100, 25)} {pct:.1f}%  ({count} orders)")

    print()
    age_brackets = [
        ("Students  18-25", df_raw[df_raw["customer_age"].between(18, 25)]),
        ("Workers   26-40", df_raw[df_raw["customer_age"].between(26, 40)]),
        ("Mid-aged  41-55", df_raw[df_raw["customer_age"].between(41, 55)]),
        ("Seniors   56-65", df_raw[df_raw["customer_age"].between(56, 65)]),
    ]
    print("  Avg spend by age group:\n")
    for label, subset in age_brackets:
        if len(subset):
            avg = subset["order_value"].mean()
            print(f"    {label}  avg spend: {avg:.0f}  {bar(avg, 1200, 20)}")

    section("SMOKE TEST COMPLETE")
    print("  Both KNN models trained and evaluated on Kaggle data.")
    print("  Ready for integration into the NaanStop Tiffin backend.")
    print()


if __name__ == "__main__":
    main()
