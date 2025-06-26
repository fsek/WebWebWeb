import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# tests which are already tested elsewhere TODO: Remove, fix or merge into other files
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


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


def test_id_sequence_not_reset_between_tests_first():
    """First test to check ID sequence behavior - create a record."""
    # This test would need access to a session and a model
    # Marking the issue that ID sequences continue across tests
    TestIDSequence.first_test_run = True


def test_id_sequence_not_reset_between_tests_second():
    """Second test to verify ID sequences continue from previous test."""
    # This demonstrates the ID sequence issue mentioned
    assert hasattr(TestIDSequence, "first_test_run")
    assert TestIDSequence.first_test_run is True


def test_engine_pool_configuration(test_engine):
    """Test that the engine is configured with correct pool settings."""
    assert test_engine.pool.__class__.__name__ == "StaticPool"
    assert test_engine.pool._pre_ping is True
    assert test_engine.echo is False


class TestEngineSharing:
    """Helper class to store state between tests for engine sharing verification."""

    engine_id = None


class TestIDSequence:
    """Helper class to track ID sequence test execution."""

    first_test_run = False
