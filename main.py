from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
from database import get_db, init_db, session_factory
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from db_models.user_model import User_DB
from schemas.schemas import UserCreate, UserCreatedResponse, UserRead
from sqlalchemy.orm import Session
from seed import seed_if_empty
from user.stuff import USERS, auth_backend, current_active_user
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
async def authenticated_route(user: Annotated[User_DB, Depends(current_active_user)]):
    return {"message": f"Hello {user.email}!"}


async def permission(user: User_DB = Depends(current_active_user), db: Session = Depends(get_db)):
    # db.query(User_DB).filter(User_DB.id == )

    a = await user.awaitable_attrs.posts
    for post in a:
        perms: list[Permission_DB] = await post.awaitable_attrs.permissions
        # for perm in perms:
        # print(1)
    # p = user.posts[0]
    # perm = p.permissions

    return user


@app.get("/perm-route")
async def perm(user: Annotated[User_DB, Depends(permission)]):
    return {"message": f"Hello {user.email}!"}
