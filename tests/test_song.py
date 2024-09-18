from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_all_songs():
    response = client.get("/")
    print(response)
    assert response.status_code == 200
