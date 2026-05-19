from pydantic import BaseModel
from typing import Literal


class TrialRequestBase(BaseModel):
    name:           str
    phone:          str
    address:        str = ""
    status:         Literal["pending", "scheduled", "completed", "declined", "no-show"] = "pending"
    requested_date: str = ""


class TrialRequestCreate(TrialRequestBase):
    pass


class TrialRequestUpdate(TrialRequestBase):
    pass


class TrialRequestOut(TrialRequestBase):
    id: str
    model_config = {"from_attributes": True}
