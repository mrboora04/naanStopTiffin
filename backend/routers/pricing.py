"""
routers/pricing.py  (v1)
========================
REST endpoints for PricingPlan resources.
Features list stored as pipe-separated strings in SQLite.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.pricing import PricingPlan
from schemas.pricing import PricingPlanCreate, PricingPlanUpdate, PricingPlanOut

router = APIRouter()
SEP = "|"


def _plan_features_to_list(obj: PricingPlan):
    """Convert pipe-separated features string → list in place."""
    if isinstance(obj.features, str):
        obj.features = [x for x in obj.features.split(SEP) if x]
    return obj


@router.get("/", response_model=dict, summary="List pricing plans (paginated)")
@limiter.limit("100/minute")
def list_plans(
    request: Request,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    dietary_type: Optional[str] = Query(None, description="Filter by dietary_type (veg, non-veg, both)"),
    db: Session = Depends(get_db),
):
    """Returns all pricing plan tiers with features listed as arrays."""
    q = db.query(PricingPlan)
    if dietary_type:
        q = q.filter(PricingPlan.dietary_type == dietary_type)
    if cursor:
        q = q.filter(PricingPlan.id > cursor)

    items = q.order_by(PricingPlan.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [PricingPlanOut.model_validate(_plan_features_to_list(p)) for p in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=PricingPlanOut, status_code=201, summary="Create a pricing plan")
@limiter.limit("100/minute")
def create_plan(request: Request, data: PricingPlanCreate, db: Session = Depends(get_db)):
    """Create a new pricing tier. Pass features as an array of strings."""
    d = data.model_dump()
    d["features"] = SEP.join(d.get("features") or [])
    obj = PricingPlan(id=str(uuid.uuid4()), **d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _plan_features_to_list(obj)


@router.get("/{plan_id}", response_model=PricingPlanOut, summary="Get a single pricing plan")
@limiter.limit("100/minute")
def get_plan(request: Request, plan_id: str, db: Session = Depends(get_db)):
    """Retrieve one pricing plan by ID."""
    obj = db.query(PricingPlan).filter(PricingPlan.id == plan_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pricing plan '{plan_id}' not found.")
    return _plan_features_to_list(obj)


@router.put("/{plan_id}", response_model=PricingPlanOut, summary="Update a pricing plan")
@limiter.limit("100/minute")
def update_plan(
    request: Request, plan_id: str, data: PricingPlanUpdate, db: Session = Depends(get_db)
):
    """Update all fields on a pricing plan."""
    obj = db.query(PricingPlan).filter(PricingPlan.id == plan_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pricing plan '{plan_id}' not found.")
    d = data.model_dump()
    d["features"] = SEP.join(d.get("features") or [])
    for k, v in d.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _plan_features_to_list(obj)


@router.delete("/{plan_id}", status_code=204, summary="Delete a pricing plan")
@limiter.limit("100/minute")
def delete_plan(request: Request, plan_id: str, db: Session = Depends(get_db)):
    """Delete a pricing plan. Returns 204 No Content."""
    obj = db.query(PricingPlan).filter(PricingPlan.id == plan_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pricing plan '{plan_id}' not found.")
    db.delete(obj)
    db.commit()
