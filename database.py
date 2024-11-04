from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import base_model
from db_models import *


# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.sqlite"
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_factory = sessionmaker(engine, expire_on_commit=False)


# A route accesses DB by "Depends()"ing on this:
def get_db():
    print("works")
    with session_factory() as session:
        yield session


DB_dependency = Annotated[Session, Depends(get_db)]


def init_db():
    base_model.BaseModel_DB.metadata.create_all(bind=engine)
