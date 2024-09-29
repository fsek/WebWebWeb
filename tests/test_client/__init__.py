from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient


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

    def get(self, path: str):
        res = self.client.get(path)
        return res.json()  # TODO: fails if empty response

    def post(self, path: str, data: dict[str, Any]):
        res = self.client.post(path, json=data)
        return res.json()
