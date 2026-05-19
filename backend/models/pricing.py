from sqlalchemy import Column, String, Float, Boolean, Text
from database import Base


class PricingPlan(Base):
    __tablename__ = "pricing_plans"

    id            = Column(String,  primary_key=True, index=True)
    name          = Column(String,  nullable=False)
    type          = Column(String,  default="monthly")   # daily | weekly | monthly
    dietary_type  = Column(String,  default="veg")       # veg | non-veg | both
    price         = Column(Float,   default=0.0)
    features      = Column(Text,    default="")          # pipe-separated list
    is_active     = Column(Boolean, default=True)
