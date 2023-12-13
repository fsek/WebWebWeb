from fastapi import Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from database import create_db_and_tables
from db_models.user_model import User_DB
from schemas.schemas import UserCreate, UserRead, UserUpdate
from user.stuff import USERS, auth_backend, current_active_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    print("")
    await create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

# Create database tables
# Note: SQLite database structre cannot be updated. Delete and run again to update


app.include_router(
    USERS.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]  # type: ignore
)
app.include_router(
    USERS.get_register_router(UserRead, UserCreate),
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
app.include_router(
    USERS.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User_DB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
