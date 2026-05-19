from sqlalchemy import Column, String, Float
from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id        = Column(String, primary_key=True, index=True)
    member_id = Column(String, nullable=False, index=True)
    amount    = Column(Float,  default=0.0)
    date      = Column(String, nullable=False)
    type      = Column(String, default="subscription")  # subscription | trial
    status    = Column(String, default="pending")       # success | pending | failed
