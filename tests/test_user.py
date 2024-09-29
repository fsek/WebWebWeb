from main import app
from tests.test_client import AuthTestClient


client = AuthTestClient(app)


def test_me():
    data = client.get("/users/me")
    print(data)


# def test_register():
#     body = UserCreate(email="test@gmail.com", first_name="Bob", last_name="Bobsson", password="password123")
#     response = client.post("/auth/register", json=body.model_dump())
#     assert response.status_code == 201
#     resp_body = response.json()
#     print(resp_body)


# def test_login():
# pass
# body = UserCreate(email="testboy@yani.com", first_name="Bob", last_name="Bobsson", password="password123")
# response = client.post(
# "password": "password123",
# "username": "testboy@gmail.com",
# },
# )
# resp_body = response.json()
# print(resp_body)
# assert response.status_code == 200
