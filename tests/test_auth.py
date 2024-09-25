from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login():
    response = client.get("/")
    print(response)
    assert response.status_code == 200


def test_register():
    response = client.get("/")
    print(response)
    assert response.status_code == 200


def test_forgot_password():
    response = client.get("/")
    print(response)
    assert response.status_code == 200


def test_reset_password():
    response = client.get("/")
    print(response)
    assert response.status_code == 200
