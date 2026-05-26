"""
routers/pilot.py  (v1)
======================
REST endpoints for PilotProgram resources.
Participants list stored as comma-separated strings in SQLite.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.pilot import PilotProgram
from schemas.pilot import PilotProgramCreate, PilotProgramUpdate, PilotProgramOut

router = APIRouter()
SEP = ","


def _participants_to_list(obj: PilotProgram):
    if isinstance(obj.participants, str):
        obj.participants = [x for x in obj.participants.split(SEP) if x]
    return obj


@router.get("/", response_model=dict, summary="List pilot programs (paginated)")
@limiter.limit("100/minute")
def list_pilots(
    request: Request,
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by program status"),
    db: Session = Depends(get_db),
):
    """Returns paginated pilot programs. Participants returned as arrays."""
    q = db.query(PilotProgram)
    if status:
        q = q.filter(PilotProgram.status == status)
    if cursor:
        q = q.filter(PilotProgram.id > cursor)

    items = q.order_by(PilotProgram.id).limit(limit + 1).all()
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [PilotProgramOut.model_validate(_participants_to_list(p)) for p in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=PilotProgramOut, status_code=201, summary="Create a pilot program")
@limiter.limit("100/minute")
def create_pilot(request: Request, data: PilotProgramCreate, db: Session = Depends(get_db)):
    """Create a new pilot program. Pass participants as an array of member IDs."""
    d = data.model_dump()
    d["participants"] = SEP.join(d.get("participants") or [])
    obj = PilotProgram(id=str(uuid.uuid4()), **d)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _participants_to_list(obj)


@router.get("/{pilot_id}", response_model=PilotProgramOut, summary="Get a single pilot program")
@limiter.limit("100/minute")
def get_pilot(request: Request, pilot_id: str, db: Session = Depends(get_db)):
    """Retrieve one pilot program by ID."""
    obj = db.query(PilotProgram).filter(PilotProgram.id == pilot_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pilot program '{pilot_id}' not found.")
    return _participants_to_list(obj)


@router.put("/{pilot_id}", response_model=PilotProgramOut, summary="Update a pilot program")
@limiter.limit("100/minute")
def update_pilot(
    request: Request, pilot_id: str, data: PilotProgramUpdate, db: Session = Depends(get_db)
):
    """Update a pilot program's details."""
    obj = db.query(PilotProgram).filter(PilotProgram.id == pilot_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pilot program '{pilot_id}' not found.")
    d = data.model_dump()
    d["participants"] = SEP.join(d.get("participants") or [])
    for k, v in d.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _participants_to_list(obj)


@router.delete("/{pilot_id}", status_code=204, summary="Delete a pilot program")
@limiter.limit("100/minute")
def delete_pilot(request: Request, pilot_id: str, db: Session = Depends(get_db)):
    """Delete a pilot program. Returns 204 No Content."""
    obj = db.query(PilotProgram).filter(PilotProgram.id == pilot_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Pilot program '{pilot_id}' not found.")
    db.delete(obj)
    db.commit()
