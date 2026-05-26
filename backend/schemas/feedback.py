from pydantic import BaseModel
from typing import Literal, Optional


class FeedbackBase(BaseModel):
    type:        Literal["feedback", "complaint", "suggestion"] = "feedback"
    rating:      int   = 5
    comments:    str   = ""
    status:      Literal["new", "resolved"] = "new"
    # ── Dish Popularity Classifier fields (Phase 4 / A_ART) ──────────────────
    member_id:   Optional[str]   = None   # who left this feedback
    delivery_id: Optional[str]   = None   # links to specific delivery
    dish_name:   str             = ""     # dish being appreciated
    liked:       bool            = False  # ❤️ tap
    tip_amount:  float           = 0.0   # tip in dollars ($)


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(FeedbackBase):
    pass


class FeedbackOut(FeedbackBase):
    id: str
    model_config = {"from_attributes": True}

