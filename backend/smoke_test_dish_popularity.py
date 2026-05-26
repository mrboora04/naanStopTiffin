"""
smoke_test_dish_popularity.py
==============================
Tests the Dish Popularity Classifier (A_ART) end-to-end with seeded feedback data.
Run: venv\Scripts\python smoke_test_dish_popularity.py
"""

import uuid
from database import SessionLocal
from models.feedback import Feedback
from ai.dish_popularity import (
    get_dish_popularity,
    get_dish_recommendation_for_member,
    train_dish_popularity_model,
)

db = SessionLocal()

# ── Seed test feedback ────────────────────────────────────────────────────────
test_data = [
    ("dal makhani",  True,  5.0, 5, "Please make this again next week!"),
    ("dal makhani",  True,  3.0, 5, "Best dal ever"),
    ("dal makhani",  False, 0.0, 4, "Lovely"),
    ("aloo gobhi",   True,  2.0, 5, "Perfect"),
    ("aloo gobhi",   False, 0.0, 3, ""),
    ("paneer tikka", True,  8.0, 5, "Kids loved it"),
    ("paneer tikka", True,  5.0, 5, "Amazing"),
    ("saag",         False, 0.0, 2, "Too salty"),
    ("saag",         False, 0.0, 1, "Did not enjoy"),
    ("rajma",        True,  1.0, 4, "Good"),
]
ids_added = []
for dish, liked, tip, rating, comment in test_data:
    fb = Feedback(
        id=str(uuid.uuid4()),
        dish_name=dish, liked=liked, tip_amount=tip,
        rating=rating, comments=comment, type="feedback"
    )
    db.add(fb)
    ids_added.append(fb.id)
db.commit()
print(f"Seeded {len(test_data)} feedback rows across {len(set(d[0] for d in test_data))} dishes")

# ── Test 1: Overall popularity ranking ───────────────────────────────────────
print()
print("=== Dish Popularity Ranking ===")
result = get_dish_popularity(db)
for d in result["dishes"]:
    status = "LOVED  " if d["schedule_recommend"] else "neutral"
    print(
        f"  [{status}] {d['dish_name']:<15}"
        f" score={d['avg_love_score']:<5}"
        f" likes={d['total_likes']}"
        f" tips=${d['total_tips_$']}"
    )
print()
print("  Summary:", result["summary"])

# ── Test 2: Train the logistic model (should succeed with 5 dishes) ───────────
print()
print("=== Train Dish Popularity Logistic Model ===")
t = train_dish_popularity_model(db)
print("  status      :", t["status"])
if t["status"] == "trained":
    print("  dish_count  :", t["dish_count"])
    print("  loved_count :", t["loved_count"])
    print("  accuracy    :", t["in_sample_accuracy"])
    print("  coefficients:")
    for k, v in t["coefficients"].items():
        print(f"    {k:<20} = {v}")
elif t["status"] == "insufficient_data":
    print("  message     :", t["message"])
else:
    print("  result      :", t)

# ── Cleanup ───────────────────────────────────────────────────────────────────
for fid in ids_added:
    fb = db.query(Feedback).filter(Feedback.id == fid).first()
    if fb:
        db.delete(fb)
db.commit()
db.close()

print()
print("=" * 45)
print("ALL TESTS COMPLETE — test data cleaned up")
