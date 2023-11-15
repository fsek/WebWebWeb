from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from sqlalchemy.engine import Engine
from sqlalchemy import event


# Temporarty because SQLite need it to enable foreign key constraint
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SQLALCHEMY_DATABASE_URL = "sqlite:///./database.sqlite"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)
DBSession = sessionmaker(engine)


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
