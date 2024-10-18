from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, session_factory
from seed import seed_if_empty
from routes import main_router
from user.permission import Permission
import os


def generate_unique_id(route: APIRoute):
    if len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    else:
        return f"{route.path}{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENV") == "development":
        # Not needed if you setup a migration system like Alembic
        init_db()
        with session_factory() as db:
            seed_if_empty(app, db)

    yield
    # after yield comes shutdown logic


# No Swagger/OpenAPI page for production
no_docs = os.getenv("ENV") == "production"

dev_origins = [
    "http://localhost",
    "http://localhost:5175",
]

app = FastAPI(
    lifespan=lifespan,
    redoc_url=None if no_docs else "/redoc",
    docs_url=None if no_docs else "/docs",
    generate_unique_id_function=generate_unique_id,
)

if os.getenv("ENV") == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=dev_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
