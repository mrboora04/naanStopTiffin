from pydantic import BaseModel
from typing import Literal


class FeedbackBase(BaseModel):
    type:     Literal["feedback", "complaint", "suggestion"] = "feedback"
    rating:   int = 5
    comments: str = ""
    status:   Literal["new", "resolved"] = "new"


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    pass


class FeedbackOut(FeedbackBase):
    id: str
    model_config = {"from_attributes": True}
