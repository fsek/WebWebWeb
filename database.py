from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db_models import *

# Temporarty because SQLite need it to enable foreign key constraint
# @event.listens_for(Any, "connect")
# def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


# SQLite database will be a single file at project root
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.sqlite"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
session_maker = sessionmaker(engine, expire_on_commit=False)


def create_db_and_tables():
    with engine.begin() as conn:
        await conn.run_sync(base_model.BaseModel_DB.metadata.create_all)  # type: ignore


# A route accesses DB by Depends()'ing on this:
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
