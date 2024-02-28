from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class CarRead(BaseSchema):
    id: int
    milage: int
    num_seats: int


class CarCreate(BaseSchema):
    id: int
    user_id: int
    user: str
    milage: int
    num_seats: int
