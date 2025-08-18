from typing import Annotated
from fastapi import Depends
import redis.asyncio as redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import base_model
from db_models import *
import os


if os.getenv("ENVIRONMENT") == "testing":
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    REDIS_URL = os.getenv("TEST_REDIS_URL")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")


if os.getenv("ENVIRONMENT") == "production":
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
    )

else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_factory = sessionmaker(engine, expire_on_commit=False)

redis_client = redis.asyncio.from_url(REDIS_URL, decode_responses=True)


def get_db():
    with session_factory() as session:
        yield session


DB_dependency = Annotated[Session, Depends(get_db)]

if os.getenv("ENVIRONMENT") == "testing":

    def get_redis():
        return redis.from_url(REDIS_URL, decode_responses=True)

else:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    def get_redis():
        return redis_client


def init_db():
    base_model.BaseModel_DB.metadata.create_all(bind=engine)
