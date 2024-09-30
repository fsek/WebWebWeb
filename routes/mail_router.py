from fastapi import APIRouter, HTTPException, status
from api_schemas.mail_schema import MailSend
from mailer.mail_sender import send_mail
from user.permission import Permission

mail_router = APIRouter()


@mail_router.post("/", dependencies=[Permission.check("manage", "Mail")])
def post_mail(data: MailSend):
    if not send_mail(data):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
