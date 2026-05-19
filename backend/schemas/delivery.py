from pydantic import BaseModel
from typing import Literal


class DeliveryBase(BaseModel):
    member_id:     str
    date:          str
    meal_type:     Literal["lunch", "dinner"] = "lunch"
    status:        Literal["scheduled", "out-for-delivery", "delivered", "failed", "skipped"] = "scheduled"
    delivery_time: str = ""
    route_order:   int = 0
    notes:         str = ""


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(DeliveryBase):
    pass


class DeliveryOut(DeliveryBase):
    id: str
    model_config = {"from_attributes": True}
