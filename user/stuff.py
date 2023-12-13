from typing import Any
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users import FastAPIUsers
from database import get_async_session
from db_models.user_model import User_DB
from user.user_manager import UserManager
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext

SECRET = "MEGA SECRET"

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[User_DB, int]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend[User_DB, int](
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase[User_DB, int](session, User_DB)


context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)


async def get_user_manager(user_db: SQLAlchemyUserDatabase[User_DB, int] = Depends(get_user_db)):
    yield UserManager(user_db, password_helper)


USERS = FastAPIUsers[User_DB, int](get_user_manager, [auth_backend])

current_active_user: Any = USERS.current_user(active=True)
