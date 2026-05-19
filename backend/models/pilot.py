from sqlalchemy import Column, String, Text
from database import Base


class PilotProgram(Base):
    __tablename__ = "pilot_programs"

    id               = Column(String, primary_key=True, index=True)
    name             = Column(String, nullable=False)
    status           = Column(String, default="planning")  # planning | active | completed | cancelled
    participants     = Column(Text,   default="")           # comma-separated member IDs
    timeline         = Column(String, default="")
    feedback_summary = Column(Text,   default="")
