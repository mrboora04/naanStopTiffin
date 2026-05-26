"""
ai/logistic_regression.py
=========================
Two binary classifiers for NaanStop Tiffin:

  1. DeliveryRiskClassifier
     — Predicts whether a delivery run will be late (>60 min) or on-track.
     — Features: route_order, day_of_week (encoded), stop_count_that_day
     — Training signal: historical `deliveries` rows where was_late is set
     — Falls back to OLS threshold if insufficient training data (<10 labeled rows)

  2. AllergyAlertClassifier  
     — Checks if tomorrow's scheduled dishes conflict with a member's allergies.
     — Uses keyword matching today → graduates to trained model when data grows.
     — Safety-first: threshold tuned low (conflict if ANY keyword overlap found).

Both classifiers:
  - Persist trained models to disk via joblib (ai/models/ directory)
  - Retrain automatically when called with insufficient cached model
  - Are stateless from the FastAPI layer's perspective (call → result)

Based on concepts from:
  - IBM ML Lab 1 (OLS foundation, cited in linear_regression.py)
  - David R. Cox (1958) — logistic regression for binary sequences
  - scikit-learn LogisticRegression docs
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from models.delivery import Delivery
from models.member import Member
from models.schedule import ScheduleDay
from ai.linear_regression import get_live_predictions

logger = logging.getLogger("naanstop.ai.logistic")

# ── Paths ─────────────────────────────────────────────────────────────────────

_MODULE_DIR   = os.path.dirname(__file__)
_MODELS_DIR   = os.path.join(_MODULE_DIR, "saved_models")
_DELIVERY_MODEL_PATH = os.path.join(_MODELS_DIR, "delivery_risk_classifier.pkl")
_SCALER_PATH         = os.path.join(_MODELS_DIR, "delivery_risk_scaler.pkl")
os.makedirs(_MODELS_DIR, exist_ok=True)

# ── Day-of-week encoding ──────────────────────────────────────────────────────

_DOW_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

def _encode_day(day_str: str) -> int:
    """Encodes a day-of-week string to an integer 0–6 (Mon=0). Defaults to 0."""
    return _DOW_MAP.get((day_str or "").lower().strip(), 0)


# ══════════════════════════════════════════════════════════════════════════════
# 1. DELIVERY RISK CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

# Threshold in minutes — deliveries beyond this are labeled "late"
LATE_THRESHOLD_MINUTES: float = 60.0

# Minimum labeled rows needed to train the real LogisticRegression model.
# Below this we fall back to the OLS-based threshold classifier.
MIN_TRAINING_ROWS = 10


def _build_delivery_features(route_order: int, day_of_week: str, stop_count: int) -> list:
    """Returns a single feature vector [route_order, day_encoded, stop_count]."""
    return [float(route_order), float(_encode_day(day_of_week)), float(stop_count)]


def train_delivery_risk_model(db: Session) -> dict:
    """
    Trains a LogisticRegression model on labeled delivery history.

    Labeled rows are those where `was_late` is not NULL.
    Features: route_order, day_of_week (encoded), stop_count_that_day.
    Label: was_late (1 = late, 0 = on-time).

    Persists the trained model + scaler to disk via joblib.
    Returns a training summary dict.
    """
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        import joblib
    except ImportError:
        return {"error": "scikit-learn or joblib not installed. Run: pip install scikit-learn joblib"}

    # 1. Pull labeled rows
    labeled = (
        db.query(Delivery)
        .filter(Delivery.was_late.isnot(None))
        .all()
    )

    if len(labeled) < MIN_TRAINING_ROWS:
        return {
            "status": "insufficient_data",
            "labeled_rows": len(labeled),
            "required": MIN_TRAINING_ROWS,
            "message": (
                f"Need {MIN_TRAINING_ROWS} labeled deliveries (with was_late set). "
                f"Currently have {len(labeled)}. Using OLS fallback until then."
            ),
        }

    # 2. Build feature matrix
    # Count deliveries per date to get stop_count context
    from collections import Counter
    date_counts = Counter(d.date for d in labeled)

    X, y = [], []
    for d in labeled:
        stop_count = date_counts[d.date]
        features = _build_delivery_features(d.route_order, d.day_of_week or "", stop_count)
        X.append(features)
        y.append(1 if d.was_late else 0)

    # 3. Scale + train
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)

    # 4. Persist
    import joblib
    joblib.dump(model,  _DELIVERY_MODEL_PATH)
    joblib.dump(scaler, _SCALER_PATH)

    # 5. Training metrics (in-sample accuracy — quick sanity check)
    accuracy = model.score(X_scaled, y)
    n_late   = sum(y)
    n_total  = len(y)

    logger.info(
        "Delivery risk model trained: %d rows, %.1f%% accuracy, %d late / %d total",
        n_total, accuracy * 100, n_late, n_total
    )

    return {
        "status": "trained",
        "labeled_rows": n_total,
        "late_count": n_late,
        "on_time_count": n_total - n_late,
        "in_sample_accuracy": round(accuracy, 4),
        "model_path": _DELIVERY_MODEL_PATH,
        "features": ["route_order", "day_of_week_encoded", "stop_count_that_day"],
        "coefficients": {
            "route_order":          round(model.coef_[0][0], 4),
            "day_of_week_encoded":  round(model.coef_[0][1], 4),
            "stop_count_that_day":  round(model.coef_[0][2], 4),
            "intercept":            round(model.intercept_[0], 4),
        },
    }


def predict_delivery_risk(
    route_order: int,
    day_of_week: str,
    stop_count: int,
    member_tier: str,
    db: Session,
) -> dict:
    """
    Predicts delivery risk for a given stop position.

    Strategy (in priority order):
      1. If a trained model exists on disk → use it (LogisticRegression)
      2. If no trained model → fall back to OLS output + LATE_THRESHOLD_MINUTES
         (This is the "smart implementation" from the TEWA T_TOPIC)

    member_tier:
      - "premium"  → lower alert threshold (0.35) — working professionals need precision
      - "standard" → higher alert threshold (0.60) — regular tiffin customers are flexible

    Returns a prediction dict with risk classification + probability.
    """
    # Threshold by user tier (Discovery #3 from E_EXPERIENCE)
    alert_threshold = 0.35 if member_tier == "premium" else 0.60

    # ── Path 1: Trained LogisticRegression model ──────────────────────────────
    if os.path.exists(_DELIVERY_MODEL_PATH) and os.path.exists(_SCALER_PATH):
        try:
            import joblib
            model  = joblib.load(_DELIVERY_MODEL_PATH)
            scaler = joblib.load(_SCALER_PATH)

            features = _build_delivery_features(route_order, day_of_week, stop_count)
            X_scaled = scaler.transform([features])

            prob_late = float(model.predict_proba(X_scaled)[0][1])
            is_at_risk = prob_late >= alert_threshold

            return {
                "route_order":      route_order,
                "day_of_week":      day_of_week,
                "stop_count":       stop_count,
                "member_tier":      member_tier,
                "probability_late": round(prob_late, 4),
                "alert_threshold":  alert_threshold,
                "delivery_risk":    "at_risk" if is_at_risk else "on_track",
                "model_type":       "logistic_regression",
                "action": (
                    "Send proactive delay notification to member" if is_at_risk
                    else "No action required"
                ),
            }
        except Exception as e:
            logger.warning("Logistic model load/predict failed (%s) — falling back to OLS.", e)

    # ── Path 2: OLS fallback (smart implementation) ───────────────────────────
    ols_result = get_live_predictions(route_order, db)
    predicted_minutes = ols_result.get("predicted_travel_time_minutes", 0.0)
    is_at_risk = predicted_minutes > LATE_THRESHOLD_MINUTES

    return {
        "route_order":              route_order,
        "day_of_week":              day_of_week,
        "stop_count":               stop_count,
        "member_tier":              member_tier,
        "predicted_minutes":        predicted_minutes,
        "late_threshold_minutes":   LATE_THRESHOLD_MINUTES,
        "delivery_risk":            "at_risk" if is_at_risk else "on_track",
        "model_type":               "ols_threshold_fallback",
        "ols_formula":              ols_result.get("formula_used", ""),
        "data_points_used":         ols_result.get("data_points_used", 0),
        "action": (
            "Send proactive delay notification to member" if is_at_risk
            else "No action required"
        ),
        "note": (
            f"Using OLS fallback — train the logistic model by labeling deliveries "
            f"with was_late=true/false (need {MIN_TRAINING_ROWS}+ labeled rows)."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. ALLERGY ALERT CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

# Ingredient synonym map — handles regional/common aliases
# Grows over time; this is the "edge case" the E_EXPERIENCE comparison matrix
# identified as the reason keyword matching eventually needs an ML model.
INGREDIENT_SYNONYMS: dict[str, list[str]] = {
    "dairy":   ["milk", "cream", "butter", "ghee", "paneer", "curd", "yogurt", "khoya", "mawa", "cheese"],
    "gluten":  ["wheat", "flour", "maida", "suji", "semolina", "bread", "roti", "naan", "paratha"],
    "nuts":    ["peanut", "cashew", "almond", "walnut", "pistachio", "kaju", "badam", "groundnut"],
    "soy":     ["soya", "tofu", "soy sauce"],
    "egg":     ["egg", "eggs", "mayonnaise"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster"],
    "sesame":  ["til", "sesame", "tahini"],
    "mustard": ["mustard", "sarson"],
}

def _expand_allergens(raw_allergies: str) -> list[str]:
    """
    Takes a comma-separated allergy string from the Member model
    and expands it to include all known synonyms.

    Example:
      "dairy, nuts" → ["milk", "cream", "butter", "ghee", "paneer", ..., "peanut", ...]
    """
    if not raw_allergies or not raw_allergies.strip():
        return []

    expanded = set()
    for token in raw_allergies.lower().split(","):
        token = token.strip()
        if token in INGREDIENT_SYNONYMS:
            # Expand category (e.g., "dairy" → all dairy ingredients)
            expanded.update(INGREDIENT_SYNONYMS[token])
        else:
            # Direct ingredient name (e.g., "paneer")
            expanded.add(token)

    return list(expanded)


def _parse_dish_ingredients(dish_text: str) -> list[str]:
    """
    Parses comma-separated dish names/ingredients from a ScheduleDay text field.
    Lowercases and strips whitespace.
    """
    if not dish_text:
        return []
    return [d.strip().lower() for d in dish_text.split(",") if d.strip()]


def check_allergy_conflicts(
    member_id: str,
    date: str,
    db: Session,
    alert_threshold: float = 0.30,
) -> dict:
    """
    Checks if tomorrow's scheduled dishes conflict with a member's registered allergies.

    Uses keyword-overlap classification (smart implementation).
    Expands allergy categories to ingredient synonyms before matching
    (e.g., "dairy" catches "ghee", "paneer", "cream" etc.)

    Safety-first: default alert_threshold is 0.30 (flag if ANY overlap found).
    A False Negative (missed allergen) is the critical failure mode here.

    Returns a full conflict report with recommended action options.
    """
    # 1. Load member
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return {"error": f"Member '{member_id}' not found."}

    # 2. Load schedule for the requested date
    schedule = db.query(ScheduleDay).filter(ScheduleDay.date == date).first()
    if not schedule:
        return {
            "member_id":   member_id,
            "date":        date,
            "status":      "no_schedule",
            "message":     f"No schedule found for {date}. No conflict check possible.",
            "action":      "none",
        }

    # 3. Expand member allergies → include synonyms
    expanded_allergens = _expand_allergens(member.allergies or "")

    if not expanded_allergens:
        return {
            "member_id":   member_id,
            "member_name": member.name,
            "date":        date,
            "status":      "no_allergies_on_file",
            "message":     "No allergies registered for this member.",
            "action":      "none",
        }

    # 4. Collect all dish ingredients from today's schedule
    all_dishes_raw = [
        schedule.lunch_veg_dishes    or "",
        schedule.lunch_nonveg_dishes or "",
        schedule.dinner_veg_dishes   or "",
        schedule.dinner_nonveg_dishes or "",
    ]
    all_ingredients = []
    for dish_text in all_dishes_raw:
        all_ingredients.extend(_parse_dish_ingredients(dish_text))

    # 5. Find overlaps
    conflicts_found = [
        ingredient for ingredient in all_ingredients
        if ingredient in expanded_allergens
    ]

    # Deduplicate (a dish listed twice shouldn't double-count)
    conflicts_found = list(set(conflicts_found))
    has_conflict    = len(conflicts_found) > 0

    # 6. Build resolution options (Discovery #2 from E_EXPERIENCE:
    #    cook cancellation / swap history becomes training data here)
    resolution_options = []
    if has_conflict:
        resolution_options = [
            {
                "option": "A",
                "action": "Cook prepares allergen-free alternative",
                "notes":  "Cook modifies dish or prepares a separate safe version",
            },
            {
                "option": "B",
                "action": "Customer skips this day",
                "notes":  "Day credit added to member account for use on another day",
            },
            {
                "option": "C",
                "action": "Refund if already paid",
                "notes":  "Pro-rated refund for this delivery if subscription already charged",
            },
        ]

    return {
        "member_id":            member_id,
        "member_name":          member.name,
        "date":                 date,
        "registered_allergies": member.allergies,
        "expanded_allergens":   expanded_allergens,
        "ingredients_checked":  all_ingredients,
        "conflict_detected":    has_conflict,
        "conflicting_items":    conflicts_found,
        "alert_threshold":      alert_threshold,
        "risk_level":           "HIGH" if has_conflict else "SAFE",
        "action":               "alert_cook" if has_conflict else "none",
        "resolution_options":   resolution_options,
        "cook_alert_message": (
            f"⚠️ ALLERGY ALERT — {member.name} has registered allergies that conflict with "
            f"{date}'s menu. Conflicting ingredients: {', '.join(conflicts_found)}. "
            f"Please prepare an alternative or contact the member."
            if has_conflict else None
        ),
    }


def run_allergy_check_all_members(date: str, db: Session) -> dict:
    """
    Runs allergy conflict checks for ALL active members against a given date's schedule.
    Designed to be called the evening before delivery (e.g., via a scheduled job).

    Returns:
      - members_checked: total active members scanned
      - conflicts_found: list of conflict reports for members who need action
      - clear_count: members with no conflicts
    """
    active_members = db.query(Member).filter(Member.member_status == "active").all()
    conflicts      = []
    clear_count    = 0

    for m in active_members:
        result = check_allergy_conflicts(member_id=m.id, date=date, db=db)
        if result.get("conflict_detected"):
            conflicts.append(result)
        elif result.get("status") != "no_allergies_on_file":
            clear_count += 1

    return {
        "date":             date,
        "members_checked":  len(active_members),
        "conflicts_found":  len(conflicts),
        "clear_count":      clear_count,
        "alerts":           conflicts,
        "summary": (
            f"{len(conflicts)} member(s) flagged for allergy conflict on {date}. "
            f"{clear_count} members clear."
        ),
    }
