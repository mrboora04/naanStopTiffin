from sqlalchemy import Column, String, Text
from database import Base


class TrialRequest(Base):
    __tablename__ = "trial_requests"

    id             = Column(String, primary_key=True, index=True)
    name           = Column(String, nullable=False)
    phone          = Column(String, nullable=False)
    address        = Column(Text,   default="")
    status         = Column(String, default="pending")  # pending | scheduled | completed | declined | no-show
    requested_date = Column(String, default="")
