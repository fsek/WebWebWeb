from typing import Annotated
from fastapi import Depends
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import base_model
from db_models import *
import os


# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.sqlite"
if os.getenv("ENVIRONMENT") == "testing":
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    REDIS_URL = os.getenv("TEST_REDIS_URL")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_factory = sessionmaker(engine, expire_on_commit=False)


# A route accesses DB by "Depends()"ing on this:
def get_db():
    with session_factory() as session:
        yield session


DB_dependency = Annotated[Session, Depends(get_db)]


def get_redis():
    return redis.asyncio.from_url(REDIS_URL, decode_responses=True)


def init_db():
    base_model.BaseModel_DB.metadata.create_all(bind=engine)
