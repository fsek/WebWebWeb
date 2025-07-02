# type: ignore
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import database_exists, create_database, drop_database
from fastapi.testclient import TestClient
from db_models.base_model import BaseModel_DB
from main import app
from database import get_db
from .basic_fixtures import *

# You can add an empty __init__.py if the error above is annoying

# Ensure we're in testing mode
os.environ["ENVIRONMENT"] = "testing"
# Set test database URL if not already set
TEST_DATABASE_URL = os.environ.setdefault(
    "TEST_DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/postgres_test"
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test database and tables once per test session."""
    # Clean setup - drop if exists, then create fresh
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)

    # Create engine and tables
    engine = create_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,  # Better for testing
        pool_pre_ping=True,  # Handle connection drops
        echo=False,  # Set to True for SQL debugging
    )
    BaseModel_DB.metadata.create_all(bind=engine)

    yield

    # Cleanup
    engine.dispose()
    drop_database(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def test_engine():
    """Shared database engine for the test session."""
    engine = create_engine(TEST_DATABASE_URL, poolclass=StaticPool, pool_pre_ping=True, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """
    Provide a transactional database session for each test.
    After each test, rollback the transaction to ensure tests don't affect each other.
    Note: Sequences are not reset, this proved difficult to do and is probably not necessary.
    (For example, if you create a user with ID 1, then rollback and go to the next test,
    the next user will still have ID 2.)
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    # Use autoflush=False for better control over when data is written
    Session = sessionmaker(bind=connection, expire_on_commit=False, autoflush=False)
    session = Session()

    yield session

    # Cleanup in reverse order
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client with database dependency override."""

    def get_test_db():
        yield db_session

    # Override dependency
    app.dependency_overrides[get_db] = get_test_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Ensure cleanup even if test fails
        app.dependency_overrides.clear()
