from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app


class AuthTestClient:
    def __init__(self, app: FastAPI):
        client = TestClient(app)
        self.client = client
        res = client.post("/auth/login", data={"username": "boss@fsektionen.se", "password": "dabdab"})
        resp_data = res.json()
        token = resp_data["access_token"]
        # We set the token to always be included in subsequent request.
        # If testing takes longer than token expiry time requests will start failing. In that case we need to get new token
        self.client.headers.update([("Authorization", f"Bearer {token}")])
        self.get = self.client.get
        self.post = self.client.post


client = AuthTestClient(app)


def test_me():
    response = client.get("/users/me")
    data = response.json()
    print(data)
    assert response.status_code == 200


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
