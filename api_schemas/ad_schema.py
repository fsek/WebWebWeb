from api_schemas.base_schema import BaseSchema

class AdRead(BaseSchema):
    ad_id: int
    title: str
    author: str | None
    price: int | None
    course: str | None
    author: str | None
    seller: str
    selling: bool
    condition: int
    
    
class AdCreate(BaseSchema):
    title: str
    author: str | None
    price: int | None
    course: str | None
    author: str | None
    seller: str
    selling: bool
    condition: int
    