from typing import Optional
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from db_models.user_model import User_DB


SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User_DB, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User_DB, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User_DB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User_DB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
