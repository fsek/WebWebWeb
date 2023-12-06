from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from database import create_db_and_tables
from db_models.user_model import User_DB
from db_models.council_model import Council_DB


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    print("")
    await create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

# Create database tables
# Note: SQLite database structre cannot be updated. Delete and run again to update


@app.get("/")
def root():
    return {"Web web web": "Hell yes"}
