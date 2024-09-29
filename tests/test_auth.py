from main import app
from tests.test_client import AuthTestClient

client = AuthTestClient(app)


def test_login():
    data = client.post("/auth/login", body={})


def test_register():
    data = client.get("/")


def test_forgot_password():
    data = client.get("/")


def test_reset_password():
    data = client.get("/")
