from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event


# Temporarty because SQLite need it to enable foreign key constraint
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: Any, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# SQLite database will be a single file at project root
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.sqlite"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)
DBSession = sessionmaker(engine)


# A route accesses DB by Depends()'ing on this:
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
