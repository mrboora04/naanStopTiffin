"""
routers/members.py  (v1)
========================
REST endpoints for Member resources.

Changes from v0:
  - Cursor-based pagination on GET /
  - ?status= and ?dietary= filter params
  - 204 No Content on DELETE
  - Rate limiting via slowapi
  - RFC 7807 errors via global handler in main.py
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models.member import Member
from schemas.member import MemberCreate, MemberUpdate, MemberOut

router = APIRouter()


@router.get("/", response_model=dict, summary="List members (paginated)")
@limiter.limit("100/minute")
def list_members(
    request: Request,
    cursor: Optional[str] = Query(None, description="Pagination cursor (last seen member id)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    status: Optional[str] = Query(None, description="Filter by member_status"),
    dietary: Optional[str] = Query(None, description="Filter by dietary_preference"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of members.

    **Cursor pagination:**
    On the first call, omit `cursor`. Each response includes `next_cursor`
    — pass it as `?cursor=<value>` on the next call to get the following page.

    **Filters:**
    - `?status=active` → only active members
    - `?dietary=veg` → only vegetarian members
    - Combined: `?status=active&dietary=veg`
    """
    q = db.query(Member)

    if status:
        q = q.filter(Member.member_status == status)
    if dietary:
        q = q.filter(Member.dietary_preference == dietary)

    # Cursor: filter rows after the cursor id
    if cursor:
        q = q.filter(Member.id > cursor)

    items = q.order_by(Member.id).limit(limit + 1).all()

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return {
        "items":       [MemberOut.model_validate(m) for m in items],
        "count":       len(items),
        "next_cursor": items[-1].id if has_more else None,
        "has_more":    has_more,
    }


@router.post("/", response_model=MemberOut, status_code=201, summary="Create a member")
@limiter.limit("100/minute")
def create_member(request: Request, data: MemberCreate, db: Session = Depends(get_db)):
    """Create a new member record. Returns the created member with its generated ID."""
    obj = Member(id=str(uuid.uuid4()), **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{member_id}", response_model=MemberOut, summary="Get a single member")
@limiter.limit("100/minute")
def get_member(request: Request, member_id: str, db: Session = Depends(get_db)):
    """Retrieve a member by their ID."""
    obj = db.query(Member).filter(Member.id == member_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Member '{member_id}' not found.")
    return obj


@router.put("/{member_id}", response_model=MemberOut, summary="Update a member (full replace)")
@limiter.limit("100/minute")
def update_member(
    request: Request, member_id: str, data: MemberUpdate, db: Session = Depends(get_db)
):
    """Replace all fields on a member record (PUT semantics — all fields required)."""
    obj = db.query(Member).filter(Member.id == member_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Member '{member_id}' not found.")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{member_id}", status_code=204, summary="Delete a member")
@limiter.limit("100/minute")
def delete_member(request: Request, member_id: str, db: Session = Depends(get_db)):
    """Delete a member. Returns 204 No Content on success."""
    obj = db.query(Member).filter(Member.id == member_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"Member '{member_id}' not found.")
    db.delete(obj)
    db.commit()
    # 204 = no body
