from fastapi import FastAPI
from db_models import BaseModelDB
from database import engine

app = FastAPI()

# Create database tables
BaseModelDB.metadata.create_all(engine)
# Note: SQLite database structre cannot be updated. Delete and run again to update


@app.get("/")
def root():
    return {"Welcome": "to web web web"}
