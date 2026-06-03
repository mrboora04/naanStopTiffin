"""
smoke_test_decision_tree.py
============================
Quick end-to-end verification of the Decision Tree classifiers.
Run from backend/ directory with:
    .venv\\Scripts\\python smoke_test_decision_tree.py

Tests:
  1. Train the Surplus Food Matcher
  2. Print feature importances (which features drive the splits)
  3. Print the tree structure (Entropy → Information Gain visible)
  4. Run a prediction for all members against a surplus dish
  5. Run the Subscription Fatigue Predictor for all active members
"""

import json
from database import SessionLocal
from ai.decision_tree import (
    train_surplus_matcher,
    predict_surplus_match,
    predict_subscription_fatigue,
)
from models.member import Member

db = SessionLocal()

# ── 1. Train ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("1. TRAINING SURPLUS FOOD MATCHER")
print("=" * 60)
result = train_surplus_matcher(db)
print("  status         :", result.get("status"))
print("  data_source    :", result.get("data_source"))
print("  rows trained   :", result.get("rows"))
print("  in-sample acc  :", result.get("in_sample_accuracy"))
print("  tree depth used:", result.get("tree_depth_used"))
print()

# ── 2. Feature Importances ────────────────────────────────────────────────────
print("  FEATURE IMPORTANCES (higher = more splits driven by this feature):")
importances = result.get("feature_importances", {})
for feat, score in sorted(importances.items(), key=lambda x: -x[1]):
    bar = "#" * int(score * 40)
    print(f"    {feat:<25} {score:.4f}  {bar}")

print()

# ── 3. Tree Structure ─────────────────────────────────────────────────────────
print("  DECISION TREE STRUCTURE (Entropy -> Information Gain):")
print("-" * 60)
print(result.get("tree_text", "  [tree text not available]"))
print("-" * 60)
print()

# ── 4. Flash Sale Prediction ──────────────────────────────────────────────────
print("=" * 60)
print("2. SURPLUS FLASH SALE PREDICTION")
print("   Dish: Paneer Butter Masala (veg) -- Friday")

print("=" * 60)
matches = predict_surplus_match(
    dish_name      = "Paneer Butter Masala",
    dish_diet_type = "veg",
    today_day      = "friday",
    db             = db,
    discount_pct   = 30,
)
print("  members_scanned :", matches["members_scanned"])
print("  hard_excluded   :", matches["hard_excluded"])
print("  candidates_found:", matches["candidates_found"])
print("  summary         :", matches["summary"])
print()
if matches["notify_list"]:
    print("  TOP CANDIDATE:")
    top = matches["notify_list"][0]
    print(f"    {top['member_name']} - confidence: {top['confidence']}")
    print(f"    {top['flash_message']}".encode('ascii', errors='replace').decode('ascii'))

else:
    print("  No candidates found (no active members or all filtered)")
print()

# ── 5. Subscription Fatigue ────────────────────────────────────────────────────
print("=" * 60)
print("3. SUBSCRIPTION FATIGUE CHECK (all active members)")
print("=" * 60)
active_members = db.query(Member).filter(Member.member_status == "active").all()

if not active_members:
    print("  No active members in DB.")
else:
    at_risk_count = 0
    for m in active_members:
        report = predict_subscription_fatigue(m.id, db)
        if report.get("fatigue_detected"):
            at_risk_count += 1
            print(f"  [AT RISK] {m.name:<20} | skipped: {report['skipped_last_7_days']} | rating: {report['last_rating']}")
            print(f"     action: {report['action']}")
    if at_risk_count == 0:
        print("  [OK] All active members are healthy -- no fatigue detected.")
print()

db.close()
print("=" * 60)
print("ALL SMOKE TESTS COMPLETE")
print("=" * 60)
