from sqlalchemy import Column, String, Integer, Text, Boolean, Float
from database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id          = Column(String,  primary_key=True, index=True)
    type        = Column(String,  default="feedback")  # feedback | complaint | suggestion
    rating      = Column(Integer, default=5)
    comments    = Column(Text,    default="")
    status      = Column(String,  default="new")       # new | resolved
    # ── Dish Popularity Classifier fields (Phase 4 / A_ART) ──────────────────
    member_id   = Column(String,  nullable=True, index=True)  # who left this feedback
    delivery_id = Column(String,  nullable=True, index=True)  # links to specific delivery
    dish_name   = Column(String,  default="")                  # dish being appreciated
    liked       = Column(Boolean, default=False)               # ❤️ tap
    tip_amount  = Column(Float,   default=0.0)                 # tip in dollars ($)
