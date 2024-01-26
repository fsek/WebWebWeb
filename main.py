from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import uvicorn
from database import init_db, session_factory
from seed import seed_if_empty
from routes import main_router
from user.permission import Permission
from os import environ


@asynccontextmanager
async def lifespan(app: FastAPI):
    if environ.get("ENV") == "development":
        # Not needed if you setup a migration system like Alembic
        init_db()
        with session_factory() as db:
            seed_if_empty(app, db)

    yield
    # after yield comes shutdown logic


# No Swagger/OpenAPI page for production
no_docs = environ.get("ENV") == "production"

app = FastAPI(
    lifespan=lifespan,
    redoc_url=None if no_docs else "/redoc",
    docs_url=None if no_docs else "/docs",
)

app.include_router(router=main_router)


@app.get("/")
def hello_route():
    return {"message": "Välkommen till F-Sektionens bäckend"}


@app.get("/user-only", dependencies=[Permission.base()])
def user_only():
    return {"message": "Hello, you are a user."}


@app.get("/member-only", dependencies=[Permission.member()])
def member_only():
    return {"message": "Congratz! Only members can reach this route"}


@app.get("/manage-event-only", dependencies=[Permission.require("manage", "Event")])
def permission_route():
    return {"message": "Congratz. You reached a manage:Event route"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
