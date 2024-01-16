from typing import Annotated, cast
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from fastapi_users import jwt
from database import init_db, session_factory

from db_models.permission_model import PermissionAction, PermissionTarget
from db_models.user_model import User_DB
from schemas.schemas import UserCreate, UserCreatedResponse, UserRead
from seed import seed_if_empty
from user.user_stuff import (
    SECRET,
    USERS,
    AccessTokenData,
    auth_backend,
    current_active_verified_user,
)
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    init_db()
    with session_factory() as db:
        seed_if_empty(app, db)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(USERS.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])  # type: ignore
app.include_router(
    USERS.get_register_router(UserCreatedResponse, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    USERS.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    USERS.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(router=router)


@app.get("/authenticated-route")
async def authenticated_route(user: Annotated[User_DB, Depends(current_active_verified_user)]):
    return {"message": f"Hello {user.email}!"}


# Create dependency to allow only a user with our own defined permissions
class Permission:
    @classmethod
    def base(cls):
        return Depends(current_active_verified_user)

    @classmethod
    def require(cls, action: PermissionAction, target: PermissionTarget):
        def dependency(user_and_token: tuple[User_DB, str] = Depends(current_active_verified_user)):
            user, token = user_and_token
            decoded_token = cast(AccessTokenData, jwt.decode_jwt(token, SECRET, audience=["fastapi-users:auth"]))
            user_role = f"{action}:{target}"

            if user_role not in decoded_token["roles"]:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return user

        return Depends(dependency)


@app.get("/perm-view", dependencies=[Permission.require("view", "Event")])
async def perm():
    # doing something view only
    print()


@app.get("/perm-manage", dependencies=[Permission.require("manage", "Event")])
async def perm2():
    # doing something heavier, like deleting users
    print()


@app.get("/perm-user")
async def perm3(user: Annotated[User_DB, Permission.base()]):
    # doing something heavier, like deleting users
    print(user)
