from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from db_models import base_model
from db_models import *

# Temporarty because SQLite need it to enable foreign key constraint
# @event.listens_for(Any, "connect")
# def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


# SQLite database will be a single file at project root
SQLALCHEMY_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./database.sqlite"
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.sqlite"


# async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL_ASYNC, echo=True)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

session_factory = sessionmaker(engine, expire_on_commit=False)
# async_sessionmaker = async_sessionmaker(async_engine, expire_on_commit=False)


# A route accesses DB by "Depends()"ing on this:
def get_db():
    with session_factory() as session:
        yield session


DB_dependency = Annotated[Session, Depends(get_db)]


def init_db():
    base_model.BaseModel_DB.metadata.create_all(bind=engine)
