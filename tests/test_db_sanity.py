import os
import pytest
from sqlalchemy import create_engine, text


@pytest.fixture(scope="module")
def engine():
    os.environ["ENVIRONMENT"] = "testing"
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


def test_database_setup(test_engine):  # Use the test_engine fixture
    with test_engine.connect() as conn:
        # Check that tables exist
        result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        table_count = result.fetchone()[0]
        assert table_count > 0, f"Expected tables to exist, but found {table_count}"

        # Check that all tables are empty (this is what you want for clean tests)
        tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall()
        for (table,) in tables:
            count = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()  # Added quotes for safety
            assert count == 0, f"Table {table} should be empty but has {count} rows"

        print(f"✅ Database setup correctly with {table_count} empty tables")
