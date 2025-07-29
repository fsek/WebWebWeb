from pydantic import BaseModel, EmailStr


class AliasRead(BaseModel):
    alias: EmailStr
    members: list[EmailStr]
