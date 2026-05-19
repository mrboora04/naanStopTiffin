import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.delivery import Delivery
from schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryOut
from typing import List

router = APIRouter()


@router.get("/", response_model=List[DeliveryOut])
def list_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).all()


@router.post("/", response_model=DeliveryOut, status_code=201)
def create_delivery(data: DeliveryCreate, db: Session = Depends(get_db)):
    obj = Delivery(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=DeliveryOut)
def get_delivery(id: str, db: Session = Depends(get_db)):
    obj = db.query(Delivery).filter(Delivery.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return obj


@router.put("/{id}", response_model=DeliveryOut)
def update_delivery(id: str, data: DeliveryUpdate, db: Session = Depends(get_db)):
    obj = db.query(Delivery).filter(Delivery.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Delivery not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_delivery(id: str, db: Session = Depends(get_db)):
    obj = db.query(Delivery).filter(Delivery.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
