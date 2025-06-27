# type: ignore
import pytest
import pytest_dependency
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from fastapi import status
import os

# tests which are already tested elsewhere TODO: Remove, fix or merge into other files
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# A bunch of tests which tests the capacity to test things,
# checking the test engine, session, etc.


def test_engine_creation(test_engine):
    """Test that test_engine fixture creates a valid SQLAlchemy engine."""
    assert test_engine is not None
    # Compare the components instead of the full URL string
    assert test_engine.url.host == "localhost"
    assert test_engine.url.port == 5432
    assert test_engine.url.database == "postgres_test"
    assert test_engine.url.username == "postgres"


def test_engine_connection(test_engine):
    """Test that the engine can establish database connections."""
    connection = test_engine.connect()
    assert connection is not None

    # Test a simple query
    result = connection.execute(text("SELECT 1 as test_value"))
    assert result.scalar() == 1

    connection.close()


def test_engine_shared_across_tests_first(test_engine):
    """First test to verify engine sharing - stores engine id."""
    # Store the engine id in a class variable for comparison
    TestEngineSharing.engine_id = id(test_engine)
    assert test_engine is not None


def test_engine_shared_across_tests_second(test_engine):
    """Second test to verify the same engine instance is shared."""
    # Compare with the engine id from the first test
    assert hasattr(TestEngineSharing, "engine_id")
    assert id(test_engine) == TestEngineSharing.engine_id


def test_engine_session_creation(test_engine):
    """Test that sessions can be created from the test engine."""
    Session = sessionmaker(bind=test_engine)
    session = Session()

    assert session is not None
    assert session.bind == test_engine

    # Test basic session functionality
    result = session.execute(text("SELECT 1 as test_value"))
    assert result.scalar() == 1

    session.close()


def test_engine_pool_configuration(test_engine):
    """Test that the engine is configured with correct pool settings."""
    assert test_engine.pool.__class__.__name__ == "StaticPool"
    assert test_engine.pool._pre_ping is True
    assert test_engine.echo is False


def test_database_setup(test_engine):
    with test_engine.connect() as conn:
        # Check that tables exist
        result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        table_count = result.fetchone()[0]
        assert table_count > 0, f"Expected tables to exist, but found {table_count}"

        # Check that all tables are empty (this is what you want for clean tests)
        tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall()
        for (table,) in tables:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            assert count == 0, f"Table {table} should be empty but has {count} rows"

        print(f"✅ Database setup correctly with {table_count} empty tables")


def test_db_connection(test_engine):
    os.environ["ENVIRONMENT"] = "testing"
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    print(f"Trying to connect to: {TEST_DATABASE_URL}")

    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    print("Database connection successful!")


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


# Test that the database is reset after each test

TEST_USER = {
    "email": "test1@example.com",
    "password": "Password123!",
    "first_name": "Test",
    "last_name": "User1",
    "start_year": 2023,
    "program": "F",
    "telephone_number": "+46701234567",
}


register_user_failed = False


def test_register_user(client):
    """Test user registration with valid data"""
    global register_user_failed
    try:
        response = client.post("/auth/register", json=TEST_USER)
        assert response.status_code == status.HTTP_201_CREATED
    except AssertionError:
        register_user_failed = True
        raise


def test_database_is_clean_after_previous_test(client, db_session):
    """Test that changes from previous tests don't persist"""
    if register_user_failed:
        pytest.skip("Skipping because test_register_user failed")

    # Check that the database is empty of users
    user_count_query = text("SELECT COUNT(*) FROM user_table")
    count = db_session.execute(user_count_query).scalar()

    # The count should be 0 if the database was properly rolled back
    assert count == 0, f"Expected empty user table, but found {count} users"

    # Verify we can register the same user again (which would probably fail if the user still existed)
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == status.HTTP_201_CREATED


class TestEngineSharing:
    """Helper class to store state between tests for engine sharing verification."""

    engine_id = None
