import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.member import Member
from schemas.member import MemberCreate, MemberUpdate, MemberOut
from typing import List

router = APIRouter()


@router.get("/", response_model=List[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.query(Member).all()


@router.post("/", response_model=MemberOut, status_code=201)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    obj = Member(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id}", response_model=MemberOut)
def get_member(id: str, db: Session = Depends(get_db)):
    obj = db.query(Member).filter(Member.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    return obj


@router.put("/{id}", response_model=MemberOut)
def update_member(id: str, data: MemberUpdate, db: Session = Depends(get_db)):
    obj = db.query(Member).filter(Member.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def delete_member(id: str, db: Session = Depends(get_db)):
    obj = db.query(Member).filter(Member.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
