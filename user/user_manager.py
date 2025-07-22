import os
import re
from typing import Optional, Type, Union
from fastapi import Request
from fastapi_users_pelicanq import BaseUserManager, IntegerIDMixin, InvalidPasswordException
from fastapi_users_pelicanq import schemas

from api_schemas.user_schemas import UserCreate
from db_models.user_model import User_DB
from mailer import reset_password_mailer, verification_mailer, welcome_mailer

SECRET = os.getenv("USER_MANAGER_SECRET")
if not SECRET:
    raise ValueError("USER_MANAGER_SECRET environment variable is not set. Please set it to a secure value.")


class UserManager(IntegerIDMixin, BaseUserManager[User_DB, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # TODO: Implement password validation logic here before production
    # https://fastapi-users.github.io/fastapi-users/latest/configuration/user-manager/?h=password+valida#validate_password

    async def validate_password(
        self,
        password: str,
        user: Union[schemas.UC, User_DB],
    ) -> None:

        if len(password) < 8:
            raise InvalidPasswordException(reason="Password should be at least 8 characters")

        if user.email.lower() in password.lower():
            raise InvalidPasswordException(reason="Password should not contain your e-mail")

        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise InvalidPasswordException(reason="Password must contain both letters and numbers")

        name = getattr(user, "name", None) or getattr(user, "username", None)
        if name and name.lower() in password.lower():
            raise InvalidPasswordException(reason="Password should not contain your name")

    async def on_after_register(self, user: User_DB, request: Optional[Request] = None):
        # print(f"User {user.id} has registered.")
        welcome_mailer.welcome_mailer(user)

    async def on_after_forgot_password(self, user: User_DB, token: str, request: Optional[Request] = None):
        # print(f"User {user.id} has forgot their password. Reset token: {token}")
        reset_password_mailer.reset_password_mailer(user, token)

    async def on_after_request_verify(self, user: User_DB, token: str, request: Optional[Request] = None):
        # print(f"Verification requested for user {user.id}. Verification token: {token}")
        verification_mailer.verification_mailer(user, token)
