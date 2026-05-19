from pydantic import BaseModel
from typing import Literal, List


class PricingPlanBase(BaseModel):
    name:         str
    type:         Literal["daily", "weekly", "monthly"] = "monthly"
    dietary_type: Literal["veg", "non-veg", "both"] = "veg"
    price:        float = 0.0
    features:     List[str] = []
    is_active:    bool = True


class PricingPlanCreate(PricingPlanBase):
    pass


class PricingPlanUpdate(PricingPlanBase):
    pass


class PricingPlanOut(PricingPlanBase):
    id: str
    model_config = {"from_attributes": True}
