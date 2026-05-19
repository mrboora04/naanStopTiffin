from pydantic import BaseModel
from typing import Literal, List


class PilotProgramBase(BaseModel):
    name:             str
    status:           Literal["planning", "active", "completed", "cancelled"] = "planning"
    participants:     List[str] = []
    timeline:         str = ""
    feedback_summary: str = ""


class PilotProgramCreate(PilotProgramBase):
    pass


class PilotProgramUpdate(PilotProgramBase):
    pass


class PilotProgramOut(PilotProgramBase):
    id: str
    model_config = {"from_attributes": True}
