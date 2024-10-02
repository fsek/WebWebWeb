from main import app
from tests.test_client import AuthTestClient
import jwt

from user.token_strategy import AccessTokenData

client = AuthTestClient(app)


def test_login():
    response, data = client.post(path="/auth/login", data={"username": "boss@fsektionen.se", "password": "dabdab"})
    assert response.status_code == 200
    # check the token contains correct info
    token: AccessTokenData = jwt.decode(data["access_token"], algorithms=["HS256"], options={"verify_signature": False})
    print(token)
    permissions = token["permissions"]
    expires_at = token["exp"]
    audience = token["aud"]
    user_id = token["sub"]


def test_register():
    response, data = client.post(
        "/auth/register",
        json={
            "email": "test@fmail.se",
            "first_name": "Dude",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "last_name": "Dude",
            "password": "pass",
            "program": "asdf",
        },
    )
    assert data["email"] == "test@fmail.se"
    assert response.status_code == 200


def test_forgot_password():
    data = client.get("/")


def test_reset_password():
    data = client.get("/")
