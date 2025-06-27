# type: ignore
import pytest
from sqlalchemy import text
from fastapi import status


def user_data_factory(
    email="test@example.com",
    password="Password123!",
    first_name="Test",
    last_name="User",
    start_year=2023,
    program="F",
    telephone_number="+46701234567",
):
    """Factory function to generate user data dicts."""
    return {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "start_year": start_year,
        "program": program,
        "telephone_number": telephone_number,
    }


@pytest.fixture
def user1_data():
    return user_data_factory(email="test1@example.com", last_name="User1", program="F", telephone_number="+46701234567")


@pytest.fixture
def user2_data():
    return user_data_factory(
        email="test2@example.com", last_name="User2", program="Pi", telephone_number="+46707654321"
    )


@pytest.fixture
def registered_user(client, user1_data):
    """Registers and returns user1_data."""
    client.post("/auth/register", json=user1_data)
    return user1_data


@pytest.fixture
def registered_users(client, user1_data, user2_data):
    """Registers multiple users and returns their data."""
    client.post("/auth/register", json=user1_data)
    client.post("/auth/register", json=user2_data)
    return [user1_data, user2_data]


def test_register_user(client, user1_data):
    """Test user registration with valid data"""
    response = client.post("/auth/register", json=user1_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["program"] == user1_data["program"]
    assert data["first_name"] == user1_data["first_name"]
    assert data["last_name"] == user1_data["last_name"]
    assert "id" in data


def test_register_duplicate_user(client, user1_data):
    """Test registration with duplicate email fails"""
    # Register first user
    response = client.post("/auth/register", json=user1_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Try to register again with same email
    response = client.post("/auth/register", json=user1_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_user(client, registered_user):
    """Test user login after registration"""
    # Registration happens in the fixture, so we can directly test login
    login_data = {"username": registered_user["email"], "password": registered_user["password"]}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_logout_user(client, registered_user):
    """Test user logout"""
    # Registration happens in the fixture, so we can directly test login/logout
    login_data = {"username": registered_user["email"], "password": registered_user["password"]}
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT or response.status_code == status.HTTP_200_OK


def test_register_multiple_users(client, user1_data, user2_data):
    """Test registering multiple users"""
    for user_data in [user1_data, user2_data]:
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["last_name"] == user_data["last_name"]


def test_login_multiple_users(client, registered_users):
    """Test logging in with multiple users"""
    # Users have been registered in the fixture
    for user_data in registered_users:
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
