"""
routers/ai.py
=============
AI endpoints — semantic search, similar members, reindex.

All routes live under /api/v1/ai/ (registered in main.py).

Endpoints:
  GET  /api/v1/ai/status                          → vector store stats
  GET  /api/v1/ai/menu-search?q=...&k=5           → semantic menu/schedule search
  GET  /api/v1/ai/similar-members/{member_id}     → find similar member profiles
  GET  /api/v1/ai/feedback-search?q=...&type=...  → semantic feedback search
  GET  /api/v1/ai/delivery-predict?route_order=N  → OLS delivery ETA (moved here)
  POST /api/v1/ai/reindex                         → re-run full indexing pipeline
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from middleware.rate_limit import limiter
from ai.rag_query import search_menu, find_similar_members, search_feedback, get_store_stats
from ai.pipeline import run_all_pipelines
from ai.linear_regression import get_live_predictions
from ai.logistic_regression import (
    predict_delivery_risk,
    train_delivery_risk_model,
    check_allergy_conflicts,
    run_allergy_check_all_members,
)
from ai.dish_popularity import (
    get_dish_popularity,
    get_dish_recommendation_for_member,
    train_dish_popularity_model,
)

router = APIRouter()


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/status", summary="Vector store status")
@limiter.limit("60/minute")
def ai_status(request: Request):
    """
    Returns the current state of the AI vector store:
    how many documents are indexed per collection, and which embedding
    provider is active.
    """
    return get_store_stats()


# ── Menu / Schedule Search ────────────────────────────────────────────────────

@router.get("/menu-search", summary="Semantic menu search")
@limiter.limit("60/minute")
def menu_search(
    request: Request,
    q: str,
    k: int = 5,
    date: Optional[str] = None,
):
    """
    Search the weekly schedule semantically.

    **Examples:**
    - `?q=veg+paneer+lunch` → days with veg paneer at lunch
    - `?q=non-veg+dinner&k=3` → top 3 non-veg dinner days
    - `?q=holiday+menu` → holiday days
    - `?q=veg+lunch&date=2026-05-23` → veg lunch on a specific date

    Results are ranked by semantic similarity score (higher = more relevant).
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    return search_menu(query=q.strip(), k=k, date_filter=date)


# ── Similar Members ───────────────────────────────────────────────────────────

@router.get("/similar-members/{member_id}", summary="Find similar member profiles")
@limiter.limit("60/minute")
def similar_members(
    request: Request,
    member_id: str,
    k: int = 3,
    db: Session = Depends(get_db),
):
    """
    Find members with the most similar dietary profiles and delivery preferences.

    Useful for:
    - Cook prep planning (who has same dietary restrictions?)
    - Sending targeted announcements (e.g., 'new vegan plan available')
    - Understanding your subscriber base clusters
    """
    result = find_similar_members(member_id=member_id, db=db, k=k)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Feedback Search ───────────────────────────────────────────────────────────

@router.get("/feedback-search", summary="Semantic feedback/complaint search")
@limiter.limit("60/minute")
def feedback_search(
    request: Request,
    q: str,
    k: int = 5,
    type: Optional[str] = None,
):
    """
    Search all feedback semantically — no need to read every record manually.

    **Examples:**
    - `?q=late+delivery` → all complaints/feedback mentioning delivery timing
    - `?q=too+spicy&type=complaint` → spice-related complaints specifically
    - `?q=packaging+idea&type=suggestion` → packaging suggestions

    Helps operations spot patterns before they become big problems.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    if type and type not in ("feedback", "complaint", "suggestion"):
        raise HTTPException(
            status_code=400,
            detail="'type' must be one of: feedback, complaint, suggestion",
        )
    return search_feedback(query=q.strip(), k=k, type_filter=type)


# ── Delivery ETA Prediction ───────────────────────────────────────────────────

@router.get("/delivery-predict", summary="Predict delivery ETA (OLS regression)")
@limiter.limit("60/minute")
def predict_delivery(
    request: Request,
    route_order: int,
    db: Session = Depends(get_db),
):
    """
    Predicts estimated transit time in minutes for a delivery stop position
    using a dynamically trained Ordinary Least Squares (OLS) regression model.

    Trained on historical `delivered` records in the database.
    Falls back to safe defaults when fewer than 3 data points exist.

    **Example:** `?route_order=5` → predicted minutes for the 5th stop on a route.
    """
    if route_order < 1:
        raise HTTPException(
            status_code=400,
            detail="route_order must be 1 or greater.",
        )
    return get_live_predictions(route_order, db)


# ── Delivery Risk Classification (Logistic Regression) ────────────────────────

@router.get("/delivery-risk", summary="Classify delivery run risk (late vs on-track)")
@limiter.limit("60/minute")
def delivery_risk(
    request: Request,
    route_order: int,
    day_of_week: str = "monday",
    stop_count: int = 5,
    member_tier: str = "standard",
    db: Session = Depends(get_db),
):
    """
    Classifies whether a delivery run is at risk of being late.

    Uses a trained LogisticRegression model when available (>= 10 labeled rows).
    Falls back to OLS-threshold classification automatically.

    **Parameters:**
    - `route_order` — which stop number this delivery is (1, 2, 3...)
    - `day_of_week` — e.g., "friday" (Friday routes tend to run late)
    - `stop_count`  — total number of deliveries scheduled that day
    - `member_tier` — "premium" (alert at 35% probability) or "standard" (alert at 60%)

    **Returns:** delivery_risk: "at_risk" | "on_track" + probability + recommended action
    """
    if route_order < 1:
        raise HTTPException(status_code=400, detail="route_order must be 1 or greater.")
    if member_tier not in ("premium", "standard"):
        raise HTTPException(status_code=400, detail="member_tier must be 'premium' or 'standard'.")

    return predict_delivery_risk(
        route_order=route_order,
        day_of_week=day_of_week,
        stop_count=stop_count,
        member_tier=member_tier,
        db=db,
    )


@router.post("/delivery-risk/train", summary="Train delivery risk logistic classifier")
@limiter.limit("5/minute")
def train_delivery_model(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Trains (or retrains) the delivery risk LogisticRegression model on all
    labeled delivery records (rows where `was_late` is set to true or false).

    **When to call:** After manually labeling delivery records with was_late = true/false.
    Requires at least 10 labeled rows to train. Returns a training summary with
    in-sample accuracy and feature coefficients.
    """
    return train_delivery_risk_model(db)


# ── Allergy Alert Classifier ──────────────────────────────────────────────────

@router.get("/allergy-check/{member_id}", summary="Check allergy conflicts for one member")
@limiter.limit("60/minute")
def allergy_check(
    request: Request,
    member_id: str,
    date: str,
    db: Session = Depends(get_db),
):
    """
    Checks if a member's registered allergies conflict with the scheduled menu
    on a given date.

    Uses ingredient synonym expansion (e.g., 'dairy' catches 'ghee', 'paneer',
    'cream', 'butter' automatically).

    Safety-first: flags any overlap, even low-confidence matches.

    **Parameters:**
    - `member_id` — member UUID
    - `date`      — ISO date string (e.g., "2026-05-27")

    **Returns:** conflict_detected, conflicting_items, cook_alert_message, resolution_options
    """
    return check_allergy_conflicts(member_id=member_id, date=date, db=db)


@router.get("/allergy-check-all", summary="Scan all active members for allergy conflicts on a date")
@limiter.limit("10/minute")
def allergy_check_all(
    request: Request,
    date: str,
    db: Session = Depends(get_db),
):
    """
    Runs the allergy conflict check for ALL active members against a given date's menu.

    Designed to be called the evening before delivery to give the cook
    advance warning of any allergen conflicts — before food is prepared.

    **Returns:** List of all members with conflicts + recommended resolution options.
    Cook-friendly alert messages included for each flagged member.
    """
    if not date or len(date) < 8:
        raise HTTPException(status_code=400, detail="date must be an ISO date string (e.g., '2026-05-27').")
    return run_allergy_check_all_members(date=date, db=db)



# ── Dish Popularity Classifier (A_ART) ──────────────────────────────────────────────

@router.get("/dish-popularity", summary="Rank dishes by customer love signals")
@limiter.limit("60/minute")
def dish_popularity(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Classifies all dishes by how much customers love them.

    Aggregates ❤️ likes, tips, ratings, and comments from the Feedback model
    into a love score per dish. Dishes above the threshold are classified as
    'loved' and recommended for next week's schedule.

    **Cook use case:** Open this endpoint every Sunday evening to decide what
    goes on next week's menu — let customer love guide the schedule.

    **Returns:** Ranked dish list with love scores, classification,
    total likes, total tips collected, and a plain-English cook message.
    """
    return get_dish_popularity(db=db, limit=limit)


@router.get("/dish-popularity/member/{member_id}", summary="Get a member's favourite dishes")
@limiter.limit("60/minute")
def member_dish_favourites(
    request: Request,
    member_id: str,
    top_n: int = 3,
    db: Session = Depends(get_db),
):
    """
    Returns the top dishes a specific member has shown love for
    via ❤️ likes, tips, or high ratings.

    **Cook use case:** Before planning the week, check what your top subscribers
    are craving. If Mrs. Patel always loves dal makhani, make sure it appears.

    **Returns:** Ranked favourite dishes for this member + a plain-English
    cook note suggesting what to include this week.
    """
    return get_dish_recommendation_for_member(member_id=member_id, db=db, top_n=top_n)


@router.post("/dish-popularity/train", summary="Train dish popularity logistic classifier")
@limiter.limit("5/minute")
def train_dish_model(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Trains (or retrains) the dish popularity LogisticRegression model on all
    dish-level feedback (feedback rows where dish_name is set).

    **When to call:** After collecting feedback for at least 5 distinct dishes.
    Returns training summary with feature coefficients showing which signals
    matter most (tip rate? like rate? rating?).

    Until trained, the smart weighted scoring fallback is used automatically.
    """
    return train_dish_popularity_model(db)




@router.post("/reindex", summary="Re-run AI indexing pipeline")
@limiter.limit("5/minute")
def reindex(
    request: Request,
    db: Session = Depends(get_db),
):

    """
    Triggers a full re-index of all data into the vector store.

    Run this after:
    - Bulk importing members
    - Uploading a new week's schedule
    - A large batch of feedback is added

    Rate-limited to 5 calls per minute to prevent accidental hammering.
    """
    summary = run_all_pipelines(db)
    return {
        "message": "Re-indexing complete.",
        "indexed": summary,
    }
