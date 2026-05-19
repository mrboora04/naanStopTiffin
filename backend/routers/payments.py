import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.payment import Payment
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentOut
from typing import List

router = APIRouter()


@router.get("/", response_model=List[PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


@router.post("/", response_model=PaymentOut, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    obj = Payment(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=PaymentOut)
def get_payment(id: str, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj


@router.put("/{id}", response_model=PaymentOut)
def update_payment(id: str, data: PaymentUpdate, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_payment(id: str, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
