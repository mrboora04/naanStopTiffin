"""
Schedule router — stores dish names as pipe-separated strings in the DB,
converts to/from List[str] in the Pydantic schema.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.schedule import ScheduleDay
from schemas.schedule import ScheduleDayCreate, ScheduleDayUpdate, ScheduleDayOut
from typing import List

router = APIRouter()

LIST_SEP = "|"


def _to_db(day_data: dict) -> dict:
    """Convert List[str] fields to pipe-separated strings before saving."""
    list_fields = ["lunch_veg_dishes", "lunch_nonveg_dishes", "dinner_veg_dishes", "dinner_nonveg_dishes"]
    for f in list_fields:
        day_data[f] = LIST_SEP.join(day_data[f])
    return day_data


def _from_db(obj: ScheduleDay) -> dict:
    """Convert pipe-separated strings back to lists when returning."""
    d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    list_fields = ["lunch_veg_dishes", "lunch_nonveg_dishes", "dinner_veg_dishes", "dinner_nonveg_dishes"]
    for f in list_fields:
        d[f] = [x for x in d[f].split(LIST_SEP) if x]
    return d


@router.get("/", response_model=List[ScheduleDayOut])
def list_schedule(db: Session = Depends(get_db)):
    return [_from_db(o) for o in db.query(ScheduleDay).all()]


@router.post("/", response_model=ScheduleDayOut, status_code=201)
def create_schedule_day(data: ScheduleDayCreate, db: Session = Depends(get_db)):
    obj = ScheduleDay(id=str(uuid.uuid4()), **_to_db(data.model_dump()))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _from_db(obj)


@router.get("/{id}", response_model=ScheduleDayOut)
def get_schedule_day(id: str, db: Session = Depends(get_db)):
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Schedule day not found")
    return _from_db(obj)


@router.put("/{id}", response_model=ScheduleDayOut)
def update_schedule_day(id: str, data: ScheduleDayUpdate, db: Session = Depends(get_db)):
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Schedule day not found")
    for k, v in _to_db(data.model_dump()).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _from_db(obj)


@router.delete("/{id}")
def delete_schedule_day(id: str, db: Session = Depends(get_db)):
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Schedule day not found")
    db.delete(obj)
    db.commit()
    return {"success": True}
