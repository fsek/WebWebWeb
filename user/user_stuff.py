from typing import Any
from fastapi_users_pelicanq.authentication import AuthenticationBackend, BearerTransport, CookieTransport
from fastapi_users_pelicanq.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi_users_pelicanq import FastAPIUsers
from database import get_db
from db_models.user_model import User_DB
from user.token_strategy import get_jwt_strategy, get_refresh_jwt_strategy
from user.user_manager import UserManager

# Access token is sent in the Authorization header as a Bearer token.
bearer_transport = BearerTransport(tokenUrl="auth/login")

# Refresh token is sent in a cookie.
# The cookie is set to expire in 30 days.
cookie_transport = CookieTransport(cookie_name="refresh_token", cookie_max_age=3600 * 24 * 30)

auth_backend = AuthenticationBackend[User_DB, int](
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

refresh_backend = AuthenticationBackend[User_DB, int](
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_refresh_jwt_strategy,
)


async def get_user_db(session: Session = Depends(get_db)):
    yield SQLAlchemyUserDatabase[User_DB, int](session, User_DB)


async def get_user_manager(user_db: SQLAlchemyUserDatabase[User_DB, int] = Depends(get_user_db)):
    yield UserManager(user_db)


USERS = FastAPIUsers[User_DB, int](get_user_manager, [auth_backend, refresh_backend])


def get_enabled_backends() -> list[AuthenticationBackend[User_DB, int]]:
    """
    Returns the enabled authentication backends.
    This is used to get the backends that are enabled for the current user.
    """
    return [auth_backend]


# Below are dependencies (functions to feed into Depends()).
# They validate the client to be a user who we have given a token.

current_verified_user: Any = USERS.current_user(verified=True, get_enabled_backends=get_enabled_backends)

current_verified_user_token: Any = USERS.current_user_token(verified=True, get_enabled_backends=get_enabled_backends)
