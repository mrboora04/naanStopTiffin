"""
routers/comments.py  (v1)
=========================
REST endpoints for Feedback/Comments resources.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackOut

router = APIRouter()


@router.get("/", response_model=dict, summary="List feedback (paginated)")
@limiter.limit("100/minute")
def list_feedback(
    request: Request,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by type: feedback | complaint | suggestion"),
    status: Optional[str] = Query(None, description="Filter by status: new | reviewed | resolved"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of feedback items.
    Filter by `type` to separate complaints from suggestions.
    Filter by `status` to work through the inbox.
    """
    q = db.query(Feedback)
    if type:
        q = q.filter(Feedback.type == type)
    if status:
        q = q.filter(Feedback.status == status)
    if cursor:
        q = q.filter(Feedback.id > cursor)

    items = q.order_by(Feedback.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [FeedbackOut.model_validate(f) for f in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=FeedbackOut, status_code=201, summary="Submit feedback")
@limiter.limit("100/minute")
def create_feedback(request: Request, data: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit a new feedback entry (comment, complaint, or suggestion)."""
    obj = Feedback(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{feedback_id}", response_model=FeedbackOut, summary="Get a single feedback item")
@limiter.limit("100/minute")
def get_feedback(request: Request, feedback_id: str, db: Session = Depends(get_db)):
    """Retrieve one feedback item by ID."""
    obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Feedback '{feedback_id}' not found.")
    return obj


@router.put("/{feedback_id}", response_model=FeedbackOut, summary="Update feedback")
@limiter.limit("100/minute")
def update_feedback(
    request: Request, feedback_id: str, data: FeedbackUpdate, db: Session = Depends(get_db)
):
    """Update a feedback record (e.g., mark as reviewed or resolved)."""
    obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Feedback '{feedback_id}' not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{feedback_id}", status_code=204, summary="Delete feedback")
@limiter.limit("100/minute")
def delete_feedback(request: Request, feedback_id: str, db: Session = Depends(get_db)):
    """Delete a feedback record. Returns 204 No Content."""
    obj = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Feedback '{feedback_id}' not found.")
    db.delete(obj)
    db.commit()
