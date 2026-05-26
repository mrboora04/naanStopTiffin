"""
routers/payments.py  (v1)
=========================
REST endpoints for Payment resources.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.payment import Payment
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentOut

router = APIRouter()


@router.get("/", response_model=dict, summary="List payments (paginated)")
@limiter.limit("100/minute")
def list_payments(
    request: Request,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    status: Optional[str] = Query(None, description="Filter by payment status (pending, paid, failed, refunded)"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of payment records.
    Filter by `member_id` to see all payments for one subscriber.
    Filter by `status` to find pending or failed payments.
    """
    q = db.query(Payment)
    if member_id:
        q = q.filter(Payment.member_id == member_id)
    if status:
        q = q.filter(Payment.status == status)
    if cursor:
        q = q.filter(Payment.id > cursor)

    items = q.order_by(Payment.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [PaymentOut.model_validate(p) for p in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=PaymentOut, status_code=201, summary="Record a payment")
@limiter.limit("100/minute")
def create_payment(request: Request, data: PaymentCreate, db: Session = Depends(get_db)):
    """Record a new payment for a member subscription."""
    obj = Payment(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{payment_id}", response_model=PaymentOut, summary="Get a single payment")
@limiter.limit("100/minute")
def get_payment(request: Request, payment_id: str, db: Session = Depends(get_db)):
    """Retrieve one payment record by ID."""
    obj = db.query(Payment).filter(Payment.id == payment_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Payment '{payment_id}' not found.")
    return obj


@router.put("/{payment_id}", response_model=PaymentOut, summary="Update a payment")
@limiter.limit("100/minute")
def update_payment(
    request: Request, payment_id: str, data: PaymentUpdate, db: Session = Depends(get_db)
):
    """Update a payment record (e.g., mark as paid or refunded)."""
    obj = db.query(Payment).filter(Payment.id == payment_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Payment '{payment_id}' not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{payment_id}", status_code=204, summary="Delete a payment record")
@limiter.limit("100/minute")
def delete_payment(request: Request, payment_id: str, db: Session = Depends(get_db)):
    """Delete a payment record. Returns 204 No Content."""
    obj = db.query(Payment).filter(Payment.id == payment_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Payment '{payment_id}' not found.")
    db.delete(obj)
    db.commit()
