from pydantic import BaseModel
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
    allergies:          str = ""
    delivery_notes:     str = ""
    emergency_contact:  str = ""


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    pass


class MemberOut(MemberBase):
    id: str
    model_config = {"from_attributes": True}
