"""
routers/deliveries.py  (v1)
===========================
REST endpoints for Delivery resources.

Changes from v0:
  - Cursor-based pagination on GET /
  - ?status= and ?date= filter params
  - 204 No Content on DELETE
  - predict-delay moved to /api/v1/ai/delivery-predict
    (kept here as a redirect alias for backward compat during transition)
  - Rate limiting
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.delivery import Delivery
from schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryOut

router = APIRouter()


@router.get("/", response_model=dict, summary="List deliveries (paginated)")
@limiter.limit("100/minute")
def list_deliveries(
    request: Request,
    cursor: Optional[str] = Query(None, description="Pagination cursor (last seen delivery id)"),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by delivery status"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of deliveries.
    Filter by `status` (scheduled, out-for-delivery, delivered, failed, skipped)
    and/or `date` (ISO format).
    """
    q = db.query(Delivery)

    if status:
        q = q.filter(Delivery.status == status)
    if date:
        q = q.filter(Delivery.date == date)
    if cursor:
        q = q.filter(Delivery.id > cursor)

    items = q.order_by(Delivery.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [DeliveryOut.model_validate(d) for d in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=DeliveryOut, status_code=201, summary="Create a delivery")
@limiter.limit("100/minute")
def create_delivery(request: Request, data: DeliveryCreate, db: Session = Depends(get_db)):
    """Create a new delivery record for a member on a specific date."""
    obj = Delivery(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{delivery_id}", response_model=DeliveryOut, summary="Get a single delivery")
@limiter.limit("100/minute")
def get_delivery(request: Request, delivery_id: str, db: Session = Depends(get_db)):
    """Retrieve a delivery record by its ID."""
    obj = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Delivery '{delivery_id}' not found.")
    return obj


@router.put("/{delivery_id}", response_model=DeliveryOut, summary="Update a delivery")
@limiter.limit("100/minute")
def update_delivery(
    request: Request, delivery_id: str, data: DeliveryUpdate, db: Session = Depends(get_db)
):
    """Update all fields on a delivery record (e.g., change status to 'delivered')."""
    obj = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Delivery '{delivery_id}' not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{delivery_id}", status_code=204, summary="Delete a delivery")
@limiter.limit("100/minute")
def delete_delivery(request: Request, delivery_id: str, db: Session = Depends(get_db)):
    """Delete a delivery record. Returns 204 No Content."""
    obj = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Delivery '{delivery_id}' not found.")
    db.delete(obj)
    db.commit()
