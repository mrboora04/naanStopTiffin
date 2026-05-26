"""
smoke_test_logistic.py
======================
Quick verification that both logistic classifiers work end-to-end.
Run from backend/ directory with: venv\Scripts\python smoke_test_logistic.py
"""

import json
import datetime
from database import SessionLocal
from ai.logistic_regression import (
    _expand_allergens,
    predict_delivery_risk,
    run_allergy_check_all_members,
    train_delivery_risk_model,
)

db = SessionLocal()

print("=== 1. Synonym Expansion ===")
print("dairy  ->", _expand_allergens("dairy"))
print("nuts   ->", _expand_allergens("nuts"))
print("gluten ->", _expand_allergens("gluten"))

print()
print("=== 2. Delivery Risk — stop 4, Friday, 6 stops, PREMIUM ===")
r = predict_delivery_risk(4, "friday", 6, "premium", db)
print("  risk         :", r["delivery_risk"])
print("  model_type   :", r["model_type"])
print("  action       :", r["action"])
if "predicted_minutes" in r:
    print("  predicted_min:", r["predicted_minutes"])

print()
print("=== 3. Delivery Risk — stop 1, Monday, 3 stops, STANDARD ===")
r2 = predict_delivery_risk(1, "monday", 3, "standard", db)
print("  risk         :", r2["delivery_risk"])
print("  model_type   :", r2["model_type"])

print()
print("=== 4. Train delivery model (expect insufficient_data) ===")
t = train_delivery_risk_model(db)
print("  status       :", t["status"])
print("  labeled_rows :", t["labeled_rows"])
print("  message      :", t.get("message", ""))

print()
print("=== 5. Allergy check all members — today ===")
today = datetime.date.today().isoformat()
scan = run_allergy_check_all_members(today, db)
print("  members_checked :", scan["members_checked"])
print("  conflicts_found :", scan["conflicts_found"])
print("  summary         :", scan["summary"])

db.close()
print()
print("=" * 40)
print("ALL TESTS COMPLETE")
