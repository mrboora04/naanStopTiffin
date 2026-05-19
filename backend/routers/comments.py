import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.feedback import Feedback
from schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackOut
from typing import List

router = APIRouter()


@router.get("/", response_model=List[FeedbackOut])
def list_feedback(db: Session = Depends(get_db)):
    return db.query(Feedback).all()


@router.post("/", response_model=FeedbackOut, status_code=201)
def create_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    obj = Feedback(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=FeedbackOut)
def get_feedback(id: str, db: Session = Depends(get_db)):
    obj = db.query(Feedback).filter(Feedback.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return obj


@router.put("/{id}", response_model=FeedbackOut)
def update_feedback(id: str, data: FeedbackUpdate, db: Session = Depends(get_db)):
    obj = db.query(Feedback).filter(Feedback.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_feedback(id: str, db: Session = Depends(get_db)):
    obj = db.query(Feedback).filter(Feedback.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
