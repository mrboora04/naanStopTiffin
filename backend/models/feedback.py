from sqlalchemy import Column, String, Integer, Text
from database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id       = Column(String,  primary_key=True, index=True)
    type     = Column(String,  default="feedback")  # feedback | complaint | suggestion
    rating   = Column(Integer, default=5)
    comments = Column(Text,    default="")
    status   = Column(String,  default="new")       # new | resolved
