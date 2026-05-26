"""
ai/dish_popularity.py
=====================
Dish Popularity Classifier — the A_ART logistic regression classifier.

Answers one question, asked weekly:
  "Did customers love this dish enough to schedule it again next week?"

This is logistic regression in service of JOY — not operations.
The training signal is organic: customer behaviour IS the label.
  liked=True + tip_amount>0 + positive comment → positive class (schedule again)
  rating<=2 + negative comment → negative class (reconsider)

Reads from the enriched Feedback model (member_id, dish_name, liked, tip_amount).

Based on concepts from:
  - A_ART insight: "The WhatsApp message you sent the cook when food was amazing"
  - David R. Cox (1958) — logistic regression for binary sequences
  - scikit-learn LogisticRegression docs
"""

import os
import logging
from collections import defaultdict
from typing import Optional

from sqlalchemy.orm import Session
from models.feedback import Feedback
from models.schedule import ScheduleDay

logger = logging.getLogger("naanstop.ai.dish_popularity")

# ── Paths ─────────────────────────────────────────────────────────────────────

_MODULE_DIR  = os.path.dirname(__file__)
_MODELS_DIR  = os.path.join(_MODULE_DIR, "saved_models")
_MODEL_PATH  = os.path.join(_MODELS_DIR, "dish_popularity_classifier.pkl")
_SCALER_PATH = os.path.join(_MODELS_DIR, "dish_popularity_scaler.pkl")
os.makedirs(_MODELS_DIR, exist_ok=True)

# ── Scoring weights (smart implementation — no training needed) ───────────────
# Each signal contributes to a composite "love score" for a dish.
# These weights represent the business logic:
#   a tip is a stronger signal than a like alone;
#   a 5-star rating with a comment is stronger than a silent rating.

WEIGHT_LIKED      = 2.0   # ❤️ tap — explicit act of appreciation
WEIGHT_TIP_BASE   = 3.0   # any tip at all — money = strong signal
WEIGHT_TIP_PER_DOLLAR = 0.5   # additional weight per dollar tipped
WEIGHT_RATING_5   = 2.0   # 5-star rating
WEIGHT_RATING_4   = 1.0   # 4-star rating
WEIGHT_RATING_1_2 = -3.0  # 1-2 star = strong negative signal
WEIGHT_COMMENT    = 0.5   # left any comment at all

# Threshold: dishes above this score are recommended for scheduling
SCHEDULE_THRESHOLD = 3.0

# Minimum feedback entries required before making a recommendation
MIN_FEEDBACK_COUNT = 1


# ══════════════════════════════════════════════════════════════════════════════
# SMART IMPLEMENTATION — Weighted scoring (no training loop needed)
# ══════════════════════════════════════════════════════════════════════════════

def _score_feedback_item(fb: Feedback) -> float:
    """
    Computes a love score for a single feedback item.
    Returns a float — higher = more loved by this customer.
    """
    score = 0.0

    if fb.liked:
        score += WEIGHT_LIKED

    if fb.tip_amount and fb.tip_amount > 0:
        score += WEIGHT_TIP_BASE + (fb.tip_amount * WEIGHT_TIP_PER_DOLLAR)

    if fb.rating:
        if fb.rating == 5:
            score += WEIGHT_RATING_5
        elif fb.rating == 4:
            score += WEIGHT_RATING_4
        elif fb.rating <= 2:
            score += WEIGHT_RATING_1_2

    if fb.comments and fb.comments.strip():
        score += WEIGHT_COMMENT

    return score


def get_dish_popularity(db: Session, limit: int = 10) -> dict:
    """
    Aggregates feedback signals for all dishes and classifies each as
    'loved' (schedule again) or 'neutral/disliked' (reconsider).

    Uses the smart weighted scoring approach — no training loop required.
    The logistic-style classification: score > SCHEDULE_THRESHOLD → loved.

    Returns a ranked list of dishes with their love scores,
    classification, total tips collected, and total likes.
    """
    # 1. Pull all feedback that has a dish_name attached
    all_feedback = (
        db.query(Feedback)
        .filter(Feedback.dish_name != "")
        .filter(Feedback.dish_name.isnot(None))
        .all()
    )

    if not all_feedback:
        return {
            "status":  "no_data",
            "message": (
                "No dish-level feedback found yet. "
                "Submit feedback with a dish_name to start building the popularity model."
            ),
            "dishes": [],
        }

    # 2. Aggregate per dish
    dish_scores:    dict[str, list[float]] = defaultdict(list)
    dish_likes:     dict[str, int]   = defaultdict(int)
    dish_tips:      dict[str, float] = defaultdict(float)
    dish_comments:  dict[str, int]   = defaultdict(int)
    dish_count:     dict[str, int]   = defaultdict(int)

    for fb in all_feedback:
        name = fb.dish_name.strip().lower()
        dish_scores[name].append(_score_feedback_item(fb))
        dish_count[name] += 1
        if fb.liked:
            dish_likes[name] += 1
        if fb.tip_amount and fb.tip_amount > 0:
            dish_tips[name] += fb.tip_amount
        if fb.comments and fb.comments.strip():
            dish_comments[name] += 1

    # 3. Classify each dish
    results = []
    for dish, scores in dish_scores.items():
        count = dish_count[dish]
        if count < MIN_FEEDBACK_COUNT:
            continue

        avg_score    = sum(scores) / len(scores)
        is_loved     = avg_score >= SCHEDULE_THRESHOLD
        total_tips   = round(dish_tips[dish], 2)
        total_likes  = dish_likes[dish]
        total_comments = dish_comments[dish]

        results.append({
            "dish_name":          dish,
            "feedback_count":     count,
            "avg_love_score":     round(avg_score, 2),
            "classification":     "loved" if is_loved else "neutral",
            "schedule_recommend": is_loved,
            "total_likes":        total_likes,
            "total_tips_$":       total_tips,
            "total_comments":     total_comments,
            "cook_message": (
                f"❤️ Customers love your {dish}! "
                f"{total_likes} likes, ${total_tips:.2f} in tips — consider scheduling next week."
                if is_loved else
                f"Your {dish} has {count} feedback entries — keep collecting more signals."
            ),
        })

    # 4. Sort by avg_love_score descending
    results.sort(key=lambda x: x["avg_love_score"], reverse=True)

    loved_count   = sum(1 for r in results if r["schedule_recommend"])
    neutral_count = len(results) - loved_count

    return {
        "status":             "success",
        "total_dishes":       len(results),
        "loved_count":        loved_count,
        "neutral_count":      neutral_count,
        "schedule_threshold": SCHEDULE_THRESHOLD,
        "dishes":             results[:limit],
        "summary": (
            f"{loved_count} dish(es) are loved by customers and recommended for next week's schedule. "
            f"{neutral_count} dish(es) need more feedback signals."
        ),
    }


def get_dish_recommendation_for_member(
    member_id: str,
    db: Session,
    top_n: int = 3,
) -> dict:
    """
    Returns the top dishes a specific member has shown love for
    (via ❤️, tips, or high ratings) — for personalized scheduling suggestions.

    Cook use case: "Mrs. Patel always loves aloo gobhi and dal makhani —
    make sure at least one is on the schedule this week."
    """
    from models.member import Member

    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return {"error": f"Member '{member_id}' not found."}

    member_feedback = (
        db.query(Feedback)
        .filter(Feedback.member_id == member_id)
        .filter(Feedback.dish_name != "")
        .all()
    )

    if not member_feedback:
        return {
            "member_id":   member_id,
            "member_name": member.name,
            "status":      "no_dish_feedback",
            "message":     f"{member.name} hasn't left dish-level feedback yet.",
            "favourites":  [],
        }

    # Score per dish for this member
    dish_scores: dict[str, list[float]] = defaultdict(list)
    for fb in member_feedback:
        name = fb.dish_name.strip().lower()
        dish_scores[name].append(_score_feedback_item(fb))

    ranked = sorted(
        [
            {
                "dish_name":   dish,
                "love_score":  round(sum(scores) / len(scores), 2),
                "times_rated": len(scores),
                "is_favourite": (sum(scores) / len(scores)) >= SCHEDULE_THRESHOLD,
            }
            for dish, scores in dish_scores.items()
        ],
        key=lambda x: x["love_score"],
        reverse=True,
    )

    favourites = [r for r in ranked if r["is_favourite"]][:top_n]

    return {
        "member_id":     member_id,
        "member_name":   member.name,
        "total_dishes_rated": len(ranked),
        "favourites":    favourites,
        "cook_note": (
            f"{member.name}'s favourites: {', '.join(f['dish_name'] for f in favourites)}. "
            f"Try to include at least one this week."
            if favourites else
            f"{member.name} hasn't shown strong preferences yet — keep collecting signals."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# HARD IMPLEMENTATION — Trained LogisticRegression (activates with enough data)
# ══════════════════════════════════════════════════════════════════════════════

MIN_TRAINING_DISHES = 5   # need at least 5 distinct dishes with feedback to train

def train_dish_popularity_model(db: Session) -> dict:
    """
    Trains a LogisticRegression model on dish-level feedback.

    Features per dish:
      - avg_rating        (float)
      - like_rate         (float: likes / total_feedback)
      - tip_rate          (float: feedbacks_with_tip / total_feedback)
      - avg_tip_amount    (float)
      - comment_rate      (float: feedbacks_with_comment / total_feedback)

    Label:
      - schedule_again (1 = loved, 0 = neutral/disliked)
      - Derived from the smart score: avg_score >= SCHEDULE_THRESHOLD → 1

    Persists model + scaler to disk via joblib.
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        import joblib
    except ImportError:
        return {"error": "scikit-learn or joblib not installed."}

    # Pull all dish-grouped feedback
    all_feedback = (
        db.query(Feedback)
        .filter(Feedback.dish_name != "")
        .filter(Feedback.dish_name.isnot(None))
        .all()
    )

    if not all_feedback:
        return {"status": "no_data", "message": "No dish feedback found."}

    # Aggregate features per dish
    dish_data: dict[str, dict] = defaultdict(lambda: {
        "ratings": [], "likes": 0, "tips": [], "comments": 0, "count": 0
    })

    for fb in all_feedback:
        name = fb.dish_name.strip().lower()
        dish_data[name]["count"] += 1
        if fb.rating:
            dish_data[name]["ratings"].append(fb.rating)
        if fb.liked:
            dish_data[name]["likes"] += 1
        if fb.tip_amount and fb.tip_amount > 0:
            dish_data[name]["tips"].append(fb.tip_amount)
        if fb.comments and fb.comments.strip():
            dish_data[name]["comments"] += 1

    if len(dish_data) < MIN_TRAINING_DISHES:
        return {
            "status":        "insufficient_data",
            "dish_count":    len(dish_data),
            "required":      MIN_TRAINING_DISHES,
            "message": (
                f"Need feedback for at least {MIN_TRAINING_DISHES} distinct dishes. "
                f"Currently have {len(dish_data)}. Using smart scoring fallback."
            ),
        }

    # Build feature matrix
    X, y, dish_names = [], [], []
    for dish, data in dish_data.items():
        count       = data["count"]
        avg_rating  = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 3.0
        like_rate   = data["likes"] / count
        tip_rate    = len(data["tips"]) / count
        avg_tip     = sum(data["tips"]) / len(data["tips"]) if data["tips"] else 0.0
        comment_rate = data["comments"] / count

        features = [avg_rating, like_rate, tip_rate, avg_tip, comment_rate]

        # Label: use the smart score as a proxy ground truth
        smart_scores = []
        for fb in all_feedback:
            if fb.dish_name.strip().lower() == dish:
                smart_scores.append(_score_feedback_item(fb))
        avg_smart = sum(smart_scores) / len(smart_scores) if smart_scores else 0.0
        label = 1 if avg_smart >= SCHEDULE_THRESHOLD else 0

        X.append(features)
        y.append(label)
        dish_names.append(dish)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    import joblib
    joblib.dump(model,  _MODEL_PATH)
    joblib.dump(scaler, _SCALER_PATH)

    accuracy = model.score(X_scaled, y)
    loved_count = sum(y)

    logger.info(
        "Dish popularity model trained: %d dishes, %.1f%% accuracy, %d loved",
        len(dish_names), accuracy * 100, loved_count
    )

    return {
        "status":           "trained",
        "dish_count":       len(dish_names),
        "loved_count":      loved_count,
        "neutral_count":    len(y) - loved_count,
        "in_sample_accuracy": round(accuracy, 4),
        "features":         ["avg_rating", "like_rate", "tip_rate", "avg_tip_amount", "comment_rate"],
        "coefficients": {
            "avg_rating":    round(model.coef_[0][0], 4),
            "like_rate":     round(model.coef_[0][1], 4),
            "tip_rate":      round(model.coef_[0][2], 4),
            "avg_tip_amount":round(model.coef_[0][3], 4),
            "comment_rate":  round(model.coef_[0][4], 4),
            "intercept":     round(model.intercept_[0], 4),
        },
        "model_path": _MODEL_PATH,
    }
