from pydantic import BaseModel
from typing import List


class ScheduleDayBase(BaseModel):
    date:                str
    day_of_week:         str = ""
    is_holiday:          bool = False
    special_notes:       str = ""
    lunch_veg_dishes:    List[str] = []
    lunch_nonveg_dishes: List[str] = []
    dinner_veg_dishes:   List[str] = []
    dinner_nonveg_dishes: List[str] = []


class ScheduleDayCreate(ScheduleDayBase):
    pass


class ScheduleDayUpdate(ScheduleDayBase):
    pass


class ScheduleDayOut(ScheduleDayBase):
    id: str
    model_config = {"from_attributes": True}
