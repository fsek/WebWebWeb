from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


# def test_register():
#     body = UserCreate(email="test@gmail.com", firstname="Bob", lastname="Bobsson", password="password123")
#     response = client.post("/auth/register", json=body.model_dump())
#     assert response.status_code == 201
#     resp_body = response.json()
#     print(resp_body)


# def test_login():
# pass
# body = UserCreate(email="testboy@yani.com", firstname="Bob", lastname="Bobsson", password="password123")
# response = client.post(
# "password": "password123",
# "username": "testboy@gmail.com",
# },
# )
# resp_body = response.json()
# print(resp_body)
# assert response.status_code == 200
