from typing import Any
from fastapi_users_pelicanq.authentication import AuthenticationBackend, BearerTransport
from fastapi_users_pelicanq.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi_users_pelicanq import FastAPIUsers
from database import get_db
from db_models.user_model import User_DB
from user.token_strategy import get_jwt_strategy
from user.user_manager import UserManager

bearer_transport = BearerTransport(tokenUrl="auth/login")

auth_backend = AuthenticationBackend[User_DB, int](
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db(session: Session = Depends(get_db)):
    yield SQLAlchemyUserDatabase[User_DB, int](session, User_DB)


async def get_user_manager(user_db: SQLAlchemyUserDatabase[User_DB, int] = Depends(get_user_db)):
    yield UserManager(user_db)


USERS = FastAPIUsers[User_DB, int](get_user_manager, [auth_backend])

# Below are dependencies (functions to feed into Depends()).
# They validate the client to be a user who we have given a token.

current_verified_user: Any = USERS.current_user(verified=True)

current_verified_user_token: Any = USERS.current_user_token(verified=True)
