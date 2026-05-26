"""
routers/requests.py  (v1)
=========================
REST endpoints for TrialRequest resources.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.trial_request import TrialRequest
from schemas.trial_request import TrialRequestCreate, TrialRequestUpdate, TrialRequestOut

router = APIRouter()


@router.get("/", response_model=dict, summary="List trial requests (paginated)")
@limiter.limit("100/minute")
def list_requests(
    request: Request,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by trial status (pending, scheduled, completed, declined, no-show)"),
    db: Session = Depends(get_db),
):
    """Returns a paginated list of trial requests. Filter by status to manage the inbox."""
    q = db.query(TrialRequest)
    if status:
        q = q.filter(TrialRequest.status == status)
    if cursor:
        q = q.filter(TrialRequest.id > cursor)

    items = q.order_by(TrialRequest.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [TrialRequestOut.model_validate(r) for r in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=TrialRequestOut, status_code=201, summary="Create a trial request")
@limiter.limit("100/minute")
def create_request(request: Request, data: TrialRequestCreate, db: Session = Depends(get_db)):
    """Submit a new trial meal request from a prospect."""
    obj = TrialRequest(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{req_id}", response_model=TrialRequestOut, summary="Get a single trial request")
@limiter.limit("100/minute")
def get_request(request: Request, req_id: str, db: Session = Depends(get_db)):
    """Retrieve one trial request by ID."""
    obj = db.query(TrialRequest).filter(TrialRequest.id == req_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Trial request '{req_id}' not found.")
    return obj


@router.put("/{req_id}", response_model=TrialRequestOut, summary="Update a trial request")
@limiter.limit("100/minute")
def update_request(
    request: Request, req_id: str, data: TrialRequestUpdate, db: Session = Depends(get_db)
):
    """Update a trial request (e.g., approve, decline, schedule)."""
    obj = db.query(TrialRequest).filter(TrialRequest.id == req_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Trial request '{req_id}' not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{req_id}", status_code=204, summary="Delete a trial request")
@limiter.limit("100/minute")
def delete_request(request: Request, req_id: str, db: Session = Depends(get_db)):
    """Delete a trial request. Returns 204 No Content."""
    obj = db.query(TrialRequest).filter(TrialRequest.id == req_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Trial request '{req_id}' not found.")
    db.delete(obj)
    db.commit()
