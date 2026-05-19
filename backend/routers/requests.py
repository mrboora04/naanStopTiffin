import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.trial_request import TrialRequest
from schemas.trial_request import TrialRequestCreate, TrialRequestUpdate, TrialRequestOut
from typing import List

router = APIRouter()


@router.get("/", response_model=List[TrialRequestOut])
def list_requests(db: Session = Depends(get_db)):
    return db.query(TrialRequest).all()


@router.post("/", response_model=TrialRequestOut, status_code=201)
def create_request(data: TrialRequestCreate, db: Session = Depends(get_db)):
    obj = TrialRequest(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=TrialRequestOut)
def get_request(id: str, db: Session = Depends(get_db)):
    obj = db.query(TrialRequest).filter(TrialRequest.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    return obj


@router.put("/{id}", response_model=TrialRequestOut)
def update_request(id: str, data: TrialRequestUpdate, db: Session = Depends(get_db)):
    obj = db.query(TrialRequest).filter(TrialRequest.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_request(id: str, db: Session = Depends(get_db)):
    obj = db.query(TrialRequest).filter(TrialRequest.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Request not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
