from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_DOC_AUTHOR, MAX_DOC_TITLE
from datetime import datetime

class DocumentRead(BaseSchema):
    document_id: int
    title: str
    date: datetime
    user_id: int
    is_private: bool
     
class DocumentCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    date: datetime
    user_id: int
    is_private: bool
    
class DocumentUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)] | None = None
    date: datetime | None = None
    is_private: bool