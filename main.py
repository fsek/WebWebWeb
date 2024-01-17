from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from database import init_db, session_factory
from seed import seed_if_empty
from routes import main_router
from user.permission import Permission


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    init_db()
    with session_factory() as db:
        seed_if_empty(app, db)

    yield
    # after yield comes shutdown logic


app = FastAPI(lifespan=lifespan)

app.include_router(router=main_router)


@app.get("/")
def hello_route():
    return {"message": "Welcome to F-Sektionen backend server!"}


@app.get("/user", dependencies=[Permission.base()])
def normal_user_route():
    return {"message": "Congratz! Only users can reach this route"}


@app.get("/manage-event", dependencies=[Permission.require("manage", "Event")])
def permission_route():
    return {"message": "Congratz. You reached a manage:Event route"}
