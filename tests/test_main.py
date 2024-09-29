from main import app
from tests.test_client import AuthTestClient

client = AuthTestClient(app)


def test_root():
    response = client.get("/")
    assert response is None
