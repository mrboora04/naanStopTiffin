"""
routers/schedule.py  (v1)
=========================
REST endpoints for ScheduleDay resources.

SQLite stores dish lists as pipe-separated strings ("Paneer|Dal|Rice").
The _to_db / _from_db helpers convert to/from List[str] for the API.
"""

import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.schedule import ScheduleDay
from schemas.schedule import ScheduleDayCreate, ScheduleDayUpdate, ScheduleDayOut

router = APIRouter()
LIST_SEP = "|"


def _to_db(day_data: dict) -> dict:
    """Convert List[str] → pipe-separated strings before writing to SQLite."""
    for f in ("lunch_veg_dishes", "lunch_nonveg_dishes", "dinner_veg_dishes", "dinner_nonveg_dishes"):
        val = day_data.get(f)
        if isinstance(val, list):
            day_data[f] = LIST_SEP.join(val)
    return day_data


def _from_db(obj: ScheduleDay) -> dict:
    """Convert pipe-separated strings → List[str] when reading from SQLite."""
    d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    for f in ("lunch_veg_dishes", "lunch_nonveg_dishes", "dinner_veg_dishes", "dinner_nonveg_dishes"):
        raw = d.get(f) or ""
        d[f] = [x for x in raw.split(LIST_SEP) if x]
    return d


@router.get("/", response_model=dict, summary="List schedule days (paginated)")
@limiter.limit("100/minute")
def list_schedule(
    request: Request,
    cursor: Optional[str] = Query(None, description="Pagination cursor (last seen id)"),
    limit: int = Query(20, ge=1, le=100),
    date: Optional[str] = Query(None, description="Filter by exact date (YYYY-MM-DD)"),
    holiday: Optional[bool] = Query(None, description="Filter holiday-only days"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of scheduled menu days.
    Supports filtering by exact date or holiday flag.
    Dish lists are returned as arrays (e.g., `["Paneer Curry", "Dal"]`).
    """
    q = db.query(ScheduleDay)
    if date:
        q = q.filter(ScheduleDay.date == date)
    if holiday is not None:
        q = q.filter(ScheduleDay.is_holiday == holiday)
    if cursor:
        q = q.filter(ScheduleDay.id > cursor)

    items = q.order_by(ScheduleDay.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [_from_db(o) for o in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=ScheduleDayOut, status_code=201, summary="Create a schedule day")
@limiter.limit("100/minute")
def create_schedule_day(request: Request, data: ScheduleDayCreate, db: Session = Depends(get_db)):
    """Create a new schedule day. Pass dish names as arrays; they are stored efficiently."""
    obj = ScheduleDay(id=str(uuid.uuid4()), **_to_db(data.model_dump()))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _from_db(obj)


@router.get("/{day_id}", response_model=ScheduleDayOut, summary="Get a single schedule day")
@limiter.limit("100/minute")
def get_schedule_day(request: Request, day_id: str, db: Session = Depends(get_db)):
    """Retrieve one schedule day by its ID."""
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == day_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Schedule day '{day_id}' not found.")
    return _from_db(obj)


@router.put("/{day_id}", response_model=ScheduleDayOut, summary="Update a schedule day")
@limiter.limit("100/minute")
def update_schedule_day(
    request: Request, day_id: str, data: ScheduleDayUpdate, db: Session = Depends(get_db)
):
    """Update a schedule day's menus and metadata."""
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == day_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Schedule day '{day_id}' not found.")
    for k, v in _to_db(data.model_dump()).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _from_db(obj)


@router.delete("/{day_id}", status_code=204, summary="Delete a schedule day")
@limiter.limit("100/minute")
def delete_schedule_day(request: Request, day_id: str, db: Session = Depends(get_db)):
    """Delete a schedule day. Returns 204 No Content."""
    obj = db.query(ScheduleDay).filter(ScheduleDay.id == day_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Schedule day '{day_id}' not found.")
    db.delete(obj)
    db.commit()
