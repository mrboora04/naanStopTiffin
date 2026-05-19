from sqlalchemy import Column, String, Boolean, Text
from database import Base


class ScheduleDay(Base):
    __tablename__ = "schedule_days"

    id                  = Column(String,  primary_key=True, index=True)
    date                = Column(String,  nullable=False, unique=True, index=True)
    day_of_week         = Column(String,  default="")
    is_holiday          = Column(Boolean, default=False)
    special_notes       = Column(Text,    default="")
    # Dish names stored as comma-separated strings for now (Phase 2: relational)
    lunch_veg_dishes    = Column(Text, default="")
    lunch_nonveg_dishes = Column(Text, default="")
    dinner_veg_dishes   = Column(Text, default="")
    dinner_nonveg_dishes = Column(Text, default="")
