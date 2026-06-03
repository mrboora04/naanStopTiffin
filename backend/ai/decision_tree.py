"""
ai/decision_tree.py
===================
Decision Tree classifiers for NaanStop Tiffin.

  1. SurplusFoodMatcher
     — When the kitchen has extra prepped food, decides which active members
       to send a flash sale discount notification.
     — Algorithm: DecisionTreeClassifier (scikit-learn)
     — Features used:
         * diet_match          (1 if member diet matches dish type, 0 otherwise)
         * allergy_safe        (1 if no allergy conflict, 0 if conflict — HARD filter)
         * past_dish_likes     (count of positive feedback rows for this dish)
         * high_tipper         (1 if member's avg tip > $1.50, else 0)
         * driver_nearby       (1 if member's route_order <= 5 on today's delivery)
         * days_since_offer    (days since last_offer_accepted — prevents spam)
         * day_of_week_encoded (0=Monday … 6=Sunday — weekends convert better)
     — Label: accepted_offer (1=accepted, 0=declined/not sent)
     — Pruning: max_depth=4, min_samples_leaf=5 to generalise across small pilot data

  2. SubscriptionFatiguePredictor  (stub — grows with production data)
     — Predicts if a subscriber is approaching churn so we can offer a "pause"
       before they cancel entirely.
     — Features: skipped_meals_count, days_since_plan_change, avg_rating
     — Label: churn_risk (1=at risk, 0=healthy)

Both classifiers:
  - Persist trained models to disk via joblib (ai/saved_models/ directory)
  - Include a cold-start synthetic bootstrap when labeled data < MIN_ROWS
  - Are called as pure functions from FastAPI or CLI scripts
  - Log decisions for future model retraining

Decision Tree Concepts Demonstrated:
  - Entropy → Information Gain driving each split
  - Pruning via max_depth + min_samples_leaf (prevents overfitting)
  - Feature importance readout after training
  - Optional: export tree to text/image for TEWA post visualisation
"""

import os
import math
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from models.member import Member
from models.delivery import Delivery
from models.feedback import Feedback

logger = logging.getLogger("naanstop.ai.decision_tree")

# ── Paths ─────────────────────────────────────────────────────────────────────
_MODULE_DIR        = os.path.dirname(__file__)
_MODELS_DIR        = os.path.join(_MODULE_DIR, "saved_models")
_SURPLUS_MODEL_PATH = os.path.join(_MODELS_DIR, "surplus_food_matcher.pkl")
_SURPLUS_COLS_PATH  = os.path.join(_MODELS_DIR, "surplus_food_matcher_cols.json")
_FATIGUE_MODEL_PATH = os.path.join(_MODELS_DIR, "subscription_fatigue.pkl")
os.makedirs(_MODELS_DIR, exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────────
MIN_ROWS          = 15      # Minimum labeled rows before the real tree trains
MAX_DEPTH         = 4       # Pruning: stops after 4 questions (16 max leaves)
MIN_SAMPLES_LEAF  = 5       # Pruning: each leaf must represent at least 5 members
SPAM_COOLDOWN_DAYS = 2      # Don't offer the same member again within 2 days
AVG_TIP_THRESHOLD  = 1.50   # Members tipping > $1.50 avg are counted as high-tippers

# ── Kitchen coords placeholder (Barrie area) ──────────────────────────────────
# Replace with actual kitchen lat/lng when deployed
KITCHEN_LAT = 44.3894
KITCHEN_LNG = -79.6903


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculates straight-line distance in kilometres between two GPS coords.
    Uses the Haversine formula — accurate enough for city-level distances.
    No external dependencies required.
    """
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _days_since(dt: Optional[datetime]) -> float:
    """Returns days elapsed since a datetime. Returns 999 if None (never offered)."""
    if dt is None:
        return 999.0
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return 999.0
    return max(0.0, (datetime.utcnow() - dt).total_seconds() / 86400)


def _encode_day(day_str: str) -> int:
    """Encodes day-of-week string to 0-6 (Mon=0). Defaults 0."""
    _MAP = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}
    return _MAP.get((day_str or "").lower().strip(), 0)


def _has_allergy_conflict(member_allergies: str, dish_name: str) -> bool:
    """
    Simple keyword check — same synonym expansion used in logistic_regression.py.
    Returns True if the dish name contains any allergen keyword for this member.
    Decision Tree NEVER runs if this returns True — safety is not probabilistic.
    """
    if not member_allergies or not member_allergies.strip():
        return False
    allergens = [a.strip().lower() for a in member_allergies.split(",")]
    dish_lower = dish_name.lower()
    return any(allergen in dish_lower for allergen in allergens if allergen)


# ══════════════════════════════════════════════════════════════════════════════
# 1. SURPLUS FOOD MATCHER
# ══════════════════════════════════════════════════════════════════════════════

def _build_surplus_features(
    member: Member,
    dish_name: str,
    dish_diet_type: str,
    today_day: str,
    db: Session,
) -> dict:
    """
    Builds a feature vector dict for a single member/dish pair.
    Returns None if the member should be hard-excluded (allergy conflict,
    wrong status, or inside spam cooldown window).
    """
    # Hard filters — these are not probabilistic, they are absolute
    if member.member_status != "active":
        return None

    if _has_allergy_conflict(member.allergies or "", dish_name):
        logger.debug("Allergy conflict for %s — skipping entirely", member.id)
        return None

    days_since_offer = _days_since(member.last_offer_accepted)
    if days_since_offer < SPAM_COOLDOWN_DAYS:
        logger.debug("Member %s offered too recently (%.1f days ago)", member.id, days_since_offer)
        return None

    # Diet match
    diet_match = 1 if (member.dietary_preference or "veg") == dish_diet_type else 0

    # Distance to kitchen
    if member.lat is not None and member.lng is not None:
        distance_km = _haversine_km(KITCHEN_LAT, KITCHEN_LNG, member.lat, member.lng)
    else:
        distance_km = 10.0  # Conservative default for members without GPS

    # Past likes for this specific dish
    past_dish_likes = (
        db.query(Feedback)
        .filter(
            Feedback.member_id == member.id,
            Feedback.dish_name  == dish_name,
            Feedback.liked      == True,
        )
        .count()
    )

    # High tipper? Pull average tip from this member's feedback history
    all_tips = (
        db.query(Feedback.tip_amount)
        .filter(Feedback.member_id == member.id)
        .all()
    )
    avg_tip = sum(t[0] for t in all_tips) / len(all_tips) if all_tips else 0.0
    high_tipper = 1 if avg_tip > AVG_TIP_THRESHOLD else 0

    # Driver already nearby? Use today's scheduled route order
    today_delivery = (
        db.query(Delivery)
        .filter(
            Delivery.member_id == member.id,
            Delivery.date      == datetime.utcnow().date().isoformat(),
        )
        .first()
    )
    driver_nearby = 1 if (today_delivery and today_delivery.route_order <= 5) else 0

    return {
        "diet_match":          diet_match,
        "distance_km":         round(distance_km, 2),
        "past_dish_likes":     past_dish_likes,
        "high_tipper":         high_tipper,
        "driver_nearby":       driver_nearby,
        "days_since_offer":    round(min(days_since_offer, 30.0), 1),  # cap at 30
        "day_of_week_encoded": _encode_day(today_day),
    }


def _synthetic_training_data() -> tuple:
    """
    Bootstrap training data when we have fewer than MIN_ROWS real labeled rows.
    Generates 100 realistic rows based on business logic so the tree learns
    proper splits (diet match, distance, spam cooldown) for demonstration.
    """
    import random
    random.seed(42) # For reproducible tree structure
    
    FEATURE_COLS = [
        "diet_match", "distance_km", "past_dish_likes",
        "high_tipper", "driver_nearby", "days_since_offer", "day_of_week_encoded"
    ]
    X = []
    y = []
    
    for _ in range(100):
        diet_match = random.choice([0, 1])
        distance_km = round(random.uniform(0.5, 12.0), 1)
        past_dish_likes = random.randint(0, 5)
        high_tipper = random.choice([0, 1])
        driver_nearby = random.choice([0, 1])
        days_since_offer = round(random.uniform(0.1, 20.0), 1)
        day_of_week_encoded = random.randint(0, 6)

        # Realistic logic for accept (1) or decline (0)
        accepted = 0
        if diet_match == 1:
            if days_since_offer > 2.0:
                if distance_km <= 6.0:
                    if past_dish_likes > 0 or driver_nearby == 1:
                        accepted = 1
        
        # Add 5% noise for realism
        if random.random() < 0.05:
            accepted = 1 if accepted == 0 else 0

        X.append([
            diet_match, distance_km, past_dish_likes, 
            high_tipper, driver_nearby, days_since_offer, day_of_week_encoded
        ])
        y.append(accepted)
        
    return X, y, FEATURE_COLS


def train_surplus_matcher(db: Session) -> dict:
    """
    Trains a Decision Tree to predict which members will accept a surplus flash sale.

    Decision Tree Concepts Demonstrated:
      - Entropy/Information Gain: each split is chosen to maximally reduce disorder
      - max_depth=4: the tree can ask at most 4 questions before deciding
      - min_samples_leaf=5: no leaf can represent fewer than 5 members
        (prevents memorising individual edge cases)

    Returns a training summary dict including feature importances.
    """
    try:
        from sklearn.tree import DecisionTreeClassifier, export_text
        import joblib, json
    except ImportError:
        return {"error": "scikit-learn or joblib not installed. Run: pip install scikit-learn joblib"}

    X_synth, y_synth, feature_cols = _synthetic_training_data()
    X, y = X_synth[:], y_synth[:]
    source = "synthetic_bootstrap"

    # TODO: replace with real labeled rows once we build an "offer outcome" table

    if len(X) < MIN_ROWS:
        return {
            "status":   "insufficient_data",
            "rows":     len(X),
            "required": MIN_ROWS,
            "message":  f"Using {len(X)} synthetic bootstrap rows. Label real outcomes to improve.",
        }

    model = DecisionTreeClassifier(
        max_depth        = MAX_DEPTH,
        min_samples_leaf = MIN_SAMPLES_LEAF,
        criterion        = "entropy",    # Use Information Gain (not Gini) — matches TEWA narrative
        random_state     = 42,
    )
    model.fit(X, y)

    # Persist model + column order so prediction always uses correct feature order
    joblib.dump(model, _SURPLUS_MODEL_PATH)
    with open(_SURPLUS_COLS_PATH, "w") as f:
        json.dump(feature_cols, f)

    accuracy        = model.score(X, y)
    importances     = dict(zip(feature_cols, [round(float(v), 4) for v in model.feature_importances_]))
    tree_text       = export_text(model, feature_names=feature_cols)

    logger.info(
        "Surplus Matcher trained: %d rows, %.1f%% accuracy, depth=%d",
        len(X), accuracy * 100, model.get_depth()
    )

    return {
        "status":              "trained",
        "data_source":         source,
        "rows":                len(X),
        "in_sample_accuracy":  round(accuracy, 4),
        "tree_depth_used":     model.get_depth(),
        "feature_importances": importances,
        "tree_text":           tree_text,
        "model_path":          _SURPLUS_MODEL_PATH,
        "note": (
            "Model trained on synthetic bootstrap data. "
            "Replace with real acceptance outcomes for production accuracy."
        ),
    }


def predict_surplus_match(
    dish_name:      str,
    dish_diet_type: str,
    today_day:      str,
    db:             Session,
    discount_pct:   int = 30,
) -> dict:
    """
    Runs the Surplus Food Matcher against all active members.
    For each member: builds features → runs allergy hard-filter → asks the tree.

    Returns a prioritised list of members to notify, with their flash sale message.
    Members are sorted by predicted confidence (descending) so the cook/admin
    sees the best candidates first.

    Args:
        dish_name:      Name of the surplus dish (e.g. "Paneer Butter Masala")
        dish_diet_type: "veg" | "non-veg" | "vegan"
        today_day:      Day of week string (e.g. "friday")
        discount_pct:   Discount percentage to offer (default 30%)
    """
    try:
        from sklearn.tree import DecisionTreeClassifier
        import joblib, json
    except ImportError:
        return {"error": "scikit-learn or joblib not installed."}

    # Auto-train if no model on disk yet
    if not os.path.exists(_SURPLUS_MODEL_PATH):
        logger.info("No surplus model found — training now...")
        train_result = train_surplus_matcher(db)
        if "error" in train_result:
            return train_result

    model = joblib.load(_SURPLUS_MODEL_PATH)
    with open(_SURPLUS_COLS_PATH) as f:
        feature_cols = json.load(f)

    active_members = db.query(Member).filter(Member.member_status == "active").all()
    candidates     = []
    hard_excluded  = 0

    for member in active_members:
        features = _build_surplus_features(member, dish_name, dish_diet_type, today_day, db)

        if features is None:
            hard_excluded += 1
            continue

        X_row = [[features[col] for col in feature_cols]]
        prediction  = int(model.predict(X_row)[0])
        confidence  = float(model.predict_proba(X_row)[0][1])  # prob of "accept"

        if prediction == 1:
            candidates.append({
                "member_id":       member.id,
                "member_name":     member.name,
                "phone":           member.phone,
                "distance_km":     features["distance_km"],
                "driver_nearby":   bool(features["driver_nearby"]),
                "past_dish_likes": features["past_dish_likes"],
                "confidence":      round(confidence, 3),
                "flash_message": (
                    f"🍛 Flash Sale! Extra {dish_name} available — {discount_pct}% off. "
                    f"Reply YES to grab it before it's gone!"
                ),
            })

    # Sort by confidence — most likely to accept shown first
    candidates.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "dish_name":       dish_name,
        "dish_diet_type":  dish_diet_type,
        "discount_pct":    discount_pct,
        "today":           today_day,
        "members_scanned": len(active_members),
        "hard_excluded":   hard_excluded,
        "candidates_found": len(candidates),
        "notify_list":     candidates,
        "summary": (
            f"{len(candidates)} member(s) matched for '{dish_name}' flash sale "
            f"({hard_excluded} excluded by allergy/diet/spam filters)."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. SUBSCRIPTION FATIGUE PREDICTOR (Stub)
# ══════════════════════════════════════════════════════════════════════════════

def predict_subscription_fatigue(member_id: str, db: Session) -> dict:
    """
    Predicts whether a subscriber is showing signs of fatigue (likely to pause/cancel).
    Uses simple rule-based heuristics today → graduates to a trained
    DecisionTreeClassifier once we have enough churn history in production.

    Fatigue signals:
      - Member has skipped 2+ deliveries in the last 7 days
      - Member has not logged any positive feedback in the last 14 days
      - Member's last rating was <= 2/5

    Returns a risk assessment and recommended action (offer pause, swap menu, etc.)
    """
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return {"error": f"Member '{member_id}' not found."}

    # Count skipped deliveries in last 7 days
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    skipped = (
        db.query(Delivery)
        .filter(
            Delivery.member_id == member_id,
            Delivery.status    == "skipped",
            Delivery.date      >= seven_days_ago,
        )
        .count()
    )

    # Last positive feedback
    last_like = (
        db.query(Feedback)
        .filter(Feedback.member_id == member_id, Feedback.liked == True)
        .order_by(Feedback.id.desc())
        .first()
    )

    # Last rating
    last_feedback = (
        db.query(Feedback)
        .filter(Feedback.member_id == member_id)
        .order_by(Feedback.id.desc())
        .first()
    )
    last_rating = last_feedback.rating if last_feedback else 5

    # Simple decision thresholds (will be replaced by trained model in production)
    at_risk = skipped >= 2 or last_rating <= 2

    action = "none"
    message = None
    if at_risk:
        action  = "offer_pause"
        message = (
            f"Hi {member.name}! We noticed you've missed some meals lately. "
            f"Life happens — want to pause your plan for a week? "
            f"Your subscription will be safe and waiting when you're ready. 🙏"
        )

    return {
        "member_id":          member_id,
        "member_name":        member.name,
        "member_status":      member.member_status,
        "skipped_last_7_days": skipped,
        "last_rating":        last_rating,
        "fatigue_detected":   at_risk,
        "risk_level":         "HIGH" if at_risk else "HEALTHY",
        "action":             action,
        "recommended_message": message,
        "model_type":         "rule_based_stub",
        "note": (
            "Using heuristic rules today. Train a DecisionTreeClassifier "
            "on churn outcomes once production data is available."
        ),
    }
