from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_CAR_DESC

class CarRead(BaseSchema):
    booking_id: int
    user_id: int
    description: str
    start_time: datetime
    end_time: datetime
    
class CarCreate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)] | None = None
    start_time: datetime
    end_time: datetime
    
class CarUpdate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)] | None
    start_time: datetime | None 
    end_time: datetime | None