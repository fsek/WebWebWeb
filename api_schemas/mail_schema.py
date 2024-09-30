from api_schemas.base_schema import BaseSchema


class MailSend(BaseSchema):
    sender: str
    receiver: str
    subject: str
    body: str
