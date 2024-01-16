from typing import Any, TypedDict
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi_users import FastAPIUsers
from database import get_async_session, get_db
from db_models.post_model import Post_DB
from db_models.user_model import User_DB
from user.user_manager import UserManager
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext

SECRET = "MEGA SECRET"

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# class to describe data in access token for our chosen JWT strategy
# sub and aud are defined by fastapi-users upon login and write_token
class AccessTokenData(TypedDict):
    sub: str
    aud: list[str]
    roles: list[str]  # this is our own field we add for permission system


class CustStrategy(JWTStrategy[User_DB, int]):
    # on login we add our own auth/roles data into the JWT token
    async def get_user_roles(self, user: User_DB) -> list[str]:
        # gotta load posts through .post_users here, not through .posts.
        posts: list[str] = []
        for post_user in user.post_users:
            post: Post_DB = await post_user.awaitable_attrs.post
            posts.append(post.name)
        return posts


def get_jwt_strategy() -> JWTStrategy[User_DB, int]:
    strat = CustStrategy(secret=SECRET, lifetime_seconds=3600)
    return strat


auth_backend = AuthenticationBackend[User_DB, int](
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db(session: Session = Depends(get_db)):
    yield SQLAlchemyUserDatabase[User_DB, int](session, User_DB)


context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)


async def get_user_manager(user_db: SQLAlchemyUserDatabase[User_DB, int] = Depends(get_user_db)):
    yield UserManager(user_db, password_helper)


USERS = FastAPIUsers[User_DB, int](get_user_manager, [auth_backend])

# Theses are functions to feed into Depends. They validate the current authenticated user
# current_active_user: Any = USERS.current_user_token(active=True)

current_active_verified_user: Any = USERS.current_user(active=True, verified=False)

current_active_verified_user_token: Any = USERS.current_user(active=True, verified=False)

# this one will only let through active, verified superusers
current_superuser: Any = USERS.current_user_token(active=True, verified=True, superuser=True)
