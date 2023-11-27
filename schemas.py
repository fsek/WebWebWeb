from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class ParentRead(BaseSchema):
    id: int
    # parents: list["ChildRead"]
    # If we try returning a circular reference from a route we get recursion error


class ChildRead(BaseSchema):
    id: int
    parents: list[ParentRead]


class FamilyCreate(BaseSchema):
    # TODO replace pass and implement
    pass
