from pydantic import BaseModel, ConfigDict

#Schema for the car table. Create and Read

# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model

class Car_Create(BaseSchema):
    driver_id: int
    num_seats:int
    milage: int

class Car_Read(BaseSchema):
    num_seats:int
    milage: int

