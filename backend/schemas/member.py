from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class MemberBase(BaseModel):
    name:               str
    phone:              str
    email:              str
    address:            str
    member_status:      Literal["active", "paused", "cancelled", "trial"] = "active"
    dietary_preference: Literal["veg", "non-veg", "vegan"] = "veg"
    plan_id:            Optional[str] = None
    renewal_date:       Optional[str] = None
    join_date:          Optional[str] = None
    # These are optional in the DB (NULL-able) — coerce None → ""
    allergies:          Optional[str] = ""
    delivery_notes:     Optional[str] = ""
    emergency_contact:  Optional[str] = ""

    @field_validator("allergies", "delivery_notes", "emergency_contact", mode="before")
    @classmethod
    def coerce_none_to_empty(cls, v):
        """Convert NULL DB values to empty string so API always returns a string."""
        return v if v is not None else ""


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    pass


class MemberOut(MemberBase):
    id: str
    model_config = {"from_attributes": True}

