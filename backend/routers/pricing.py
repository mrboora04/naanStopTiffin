import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.pricing import PricingPlan
from schemas.pricing import PricingPlanCreate, PricingPlanUpdate, PricingPlanOut
from typing import List

router = APIRouter()
SEP = "|"


@router.get("/", response_model=List[PricingPlanOut])
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(PricingPlan).all()
    for p in plans:
        p.features = [x for x in p.features.split(SEP) if x]
    return plans


@router.post("/", response_model=PricingPlanOut, status_code=201)
def create_plan(data: PricingPlanCreate, db: Session = Depends(get_db)):
    d = data.model_dump()
    d["features"] = SEP.join(d["features"])
    obj = PricingPlan(id=str(uuid.uuid4()), **d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    obj.features = [x for x in obj.features.split(SEP) if x]
    return obj


@router.get("/{id}", response_model=PricingPlanOut)
def get_plan(id: str, db: Session = Depends(get_db)):
    obj = db.query(PricingPlan).filter(PricingPlan.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Plan not found")
    obj.features = [x for x in obj.features.split(SEP) if x]
    return obj


@router.put("/{id}", response_model=PricingPlanOut)
def update_plan(id: str, data: PricingPlanUpdate, db: Session = Depends(get_db)):
    obj = db.query(PricingPlan).filter(PricingPlan.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Plan not found")
    d = data.model_dump()
    d["features"] = SEP.join(d["features"])
    for k, v in d.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    obj.features = [x for x in obj.features.split(SEP) if x]
    return obj


@router.delete("/{id}")
def delete_plan(id: str, db: Session = Depends(get_db)):
    obj = db.query(PricingPlan).filter(PricingPlan.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
