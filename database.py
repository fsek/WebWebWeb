from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db_models.base_model import BaseModel_DB


# Temporarty because SQLite need it to enable foreign key constraint
# @event.listens_for(Any, "connect")
# def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


# SQLite database will be a single file at project root
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./database.sqlite"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# class A(BaseModel_DB):
# __tablename__
# id: Mapped[int] = mapped_column(primary_key=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel_DB.metadata.create_all)


# A route accesses DB by Depends()'ing on this:
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
