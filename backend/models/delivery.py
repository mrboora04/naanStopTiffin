from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime
from database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id            = Column(String,  primary_key=True, index=True)
    member_id     = Column(String,  nullable=False, index=True)
    date          = Column(String,  nullable=False, index=True)
    meal_type     = Column(String,  default="lunch")      # lunch | dinner
    status        = Column(String,  default="scheduled")  # scheduled | out-for-delivery | delivered | failed | skipped
    delivery_time = Column(String,  default="")
    route_order   = Column(Integer, default=0)
    notes         = Column(Text,    default="")
    day_of_week   = Column(String,  default="")     # monday|tuesday|... (logistic regression feature)
    was_late      = Column(Boolean, nullable=True)   # NULL=unlabeled | True=late | False=on-time (training label)

    # ── Phase 2: Zero-Cost Delivery Telemetry ────────────────────────────────
    # Driver clicks "Dispatch" → records departure. Driver clicks "Done" → records arrival.
    # ML model computes actual_duration = (delivered_at - dispatched_at) automatically.
    dispatched_at        = Column(DateTime, nullable=True)   # When driver leaves the kitchen
    delivered_at         = Column(DateTime, nullable=True)   # When driver marks run complete
    estimated_drive_time = Column(Integer,  nullable=True)   # Static OSRM estimate in minutes (set at route creation)
