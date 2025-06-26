import os
from sqlalchemy import text  # <-- import text


def test_db_connection(test_engine):
    os.environ["ENVIRONMENT"] = "testing"
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    print(f"Trying to connect to: {TEST_DATABASE_URL}")

    engine = test_engine  # Use the test_engine fixture directly
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))  # <-- wrap SQL in text()
        assert result.fetchone()[0] == 1
    print("Database connection successful!")
