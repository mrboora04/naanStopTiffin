import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.pilot import PilotProgram
from schemas.pilot import PilotProgramCreate, PilotProgramUpdate, PilotProgramOut
from typing import List

router = APIRouter()
SEP = ","


@router.get("/", response_model=List[PilotProgramOut])
def list_pilots(db: Session = Depends(get_db)):
    pilots = db.query(PilotProgram).all()
    for p in pilots:
        p.participants = [x for x in p.participants.split(SEP) if x]
    return pilots


@router.post("/", response_model=PilotProgramOut, status_code=201)
def create_pilot(data: PilotProgramCreate, db: Session = Depends(get_db)):
    d = data.model_dump()
    d["participants"] = SEP.join(d["participants"])
    obj = PilotProgram(id=str(uuid.uuid4()), **d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    obj.participants = [x for x in obj.participants.split(SEP) if x]
    return obj


@router.get("/{id}", response_model=PilotProgramOut)
def get_pilot(id: str, db: Session = Depends(get_db)):
    obj = db.query(PilotProgram).filter(PilotProgram.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pilot not found")
    obj.participants = [x for x in obj.participants.split(SEP) if x]
    return obj


@router.put("/{id}", response_model=PilotProgramOut)
def update_pilot(id: str, data: PilotProgramUpdate, db: Session = Depends(get_db)):
    obj = db.query(PilotProgram).filter(PilotProgram.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pilot not found")
    d = data.model_dump()
    d["participants"] = SEP.join(d["participants"])
    for k, v in d.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    obj.participants = [x for x in obj.participants.split(SEP) if x]
    return obj


@router.delete("/{id}")
def delete_pilot(id: str, db: Session = Depends(get_db)):
    obj = db.query(PilotProgram).filter(PilotProgram.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pilot not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
