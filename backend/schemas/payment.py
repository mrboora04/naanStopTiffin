from pydantic import BaseModel
from typing import Literal


class PaymentBase(BaseModel):
    member_id: str
    amount:    float = 0.0
    date:      str
    type:      Literal["subscription", "trial"] = "subscription"
    status:    Literal["success", "pending", "failed"] = "pending"


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: str
    model_config = {"from_attributes": True}
