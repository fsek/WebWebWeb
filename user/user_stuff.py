import os
from typing import Any, cast
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, CookieTransport
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi_users import FastAPIUsers
from database import get_db
from db_models.user_model import User_DB
from user.refresh_auth_backend import RefreshAuthenticationBackend
from user.token_strategy import get_jwt_strategy, get_refresh_redis_strategy, LOGIN_TIMEOUT
from user.user_manager import UserManager


# This is such a horrible hack, but the alternative is essentially a full refactor of the code
class _AsyncSessionProxy:
    """Expose an async-session-like interface on top of a sync Session."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, instance: Any) -> None:
        self._session.add(instance)

    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        return self._session.execute(statement, *args, **kwargs)

    async def commit(self) -> None:
        self._session.commit()

    async def refresh(self, instance: Any) -> None:
        self._session.refresh(instance)

    async def delete(self, instance: Any) -> None:
        self._session.delete(instance)


# Access token is sent in the Authorization header as a Bearer token.
bearer_transport = BearerTransport(tokenUrl="auth/login")


# Refresh token is sent in a cookie.
# The cookie is set to expire in 30 days.
if os.getenv("ENVIRONMENT") == "production":
    cookie_transport = CookieTransport(
        # Secure cookie for production, with __Secure- prefix to ensure it is only sent over HTTPS
        cookie_name="__Secure-fsek_refresh_token",
        cookie_max_age=LOGIN_TIMEOUT,
        cookie_samesite="lax",
        # cookie_domain="fsektionen.se",
        cookie_path="/auth",  # Server path where the cookie is sent
        cookie_secure=True,  # Secure cookie for production
        cookie_httponly=True,  # HttpOnly to prevent JavaScript access
    )
elif os.getenv("ENVIRONMENT") == "stage":
    cookie_transport = CookieTransport(
        cookie_name="_fsek_stage_refresh_token",
        cookie_max_age=LOGIN_TIMEOUT,
        cookie_samesite="lax",
        # cookie_domain="fsektionen.se",  # Use default domain for local development
        cookie_path="/auth",
        cookie_secure=True,
        cookie_httponly=True,  # HttpOnly to prevent JavaScript access
    )
else:
    cookie_transport = CookieTransport(
        cookie_name="_fsek_refresh_token",
        cookie_max_age=LOGIN_TIMEOUT,
        cookie_samesite="lax",
        cookie_domain=None,  # Use default domain for local development
        cookie_path="/auth",
        cookie_secure=False,  # Insecure cookie for local development
        cookie_httponly=True,  # HttpOnly to prevent JavaScript access
    )

auth_backend = AuthenticationBackend[User_DB, int](
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

refresh_backend = RefreshAuthenticationBackend[User_DB, int](
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_refresh_redis_strategy,
)


async def get_user_db(session: Session = Depends(get_db)):
    async_session = cast(AsyncSession, _AsyncSessionProxy(session))
    yield SQLAlchemyUserDatabase[User_DB, int](async_session, User_DB)


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

# We want to use optional, which allows these to be None
# to allow for routes which have optional manage_permission but
# are still accessible without an account
current_user: Any = USERS.current_user(get_enabled_backends=get_enabled_backends, optional=True)

current_verified_user: Any = USERS.current_user(verified=True, get_enabled_backends=get_enabled_backends, optional=True)
