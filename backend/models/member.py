from sqlalchemy import Column, String, Text, Float, DateTime
from database import Base


class Member(Base):
    __tablename__ = "members"

    id               = Column(String, primary_key=True, index=True)
    name             = Column(String, nullable=False)
    phone            = Column(String, nullable=False)
    email            = Column(String, nullable=False)
    address          = Column(Text,   nullable=False)
    member_status    = Column(String, default="active")   # active | paused | cancelled | trial
    dietary_preference = Column(String, default="veg")    # veg | non-veg | vegan
    plan_id          = Column(String, nullable=True)
    renewal_date     = Column(String, nullable=True)
    join_date        = Column(String, nullable=True)
    allergies        = Column(Text,   default="")
    delivery_notes   = Column(Text,   default="")
    emergency_contact = Column(String, default="")

    # ── Phase 3: Decision Tree Flash Sale features ────────────────────────────
    lat                 = Column(Float,    nullable=True)   # GPS latitude  (for distance_km calc)
    lng                 = Column(Float,    nullable=True)   # GPS longitude (for distance_km calc)
    last_offer_accepted = Column(DateTime, nullable=True)   # Timestamp of last accepted flash sale
    #   NULL  = never offered
    #   Set   = model learns cadence, prevents daily spamming

