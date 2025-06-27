import pytest
from sqlalchemy import text
from fastapi import status

# Test data for multiple users
TEST_USERS = [
    {
        "email": "test1@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User1",
        "start_year": 2023,
        "program": "F",
        "telephone_number": "+46701234567",
    },
    {
        "email": "test2@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User2",
        "start_year": 2023,
        "program": "Pi",
        "telephone_number": "+46707654321",
    },
]


def test_register_user(client):
    """Test user registration with valid data"""
    response = client.post("/auth/register", json=TEST_USERS[0])
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["program"] == TEST_USERS[0]["program"]
    assert data["first_name"] == TEST_USERS[0]["first_name"]
    assert data["last_name"] == TEST_USERS[0]["last_name"]
    assert "id" in data


def test_register_duplicate_user(client):
    """Test registration with duplicate email fails"""
    # Register first user
    response = client.post("/auth/register", json=TEST_USERS[0])
    assert response.status_code == status.HTTP_201_CREATED

    # Try to register again with same email
    response = client.post("/auth/register", json=TEST_USERS[0])
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_user(client):
    """Test user login after registration"""
    # Register user
    client.post("/auth/register", json=TEST_USERS[0])

    # Login with registered user
    login_data = {"username": TEST_USERS[0]["email"], "password": TEST_USERS[0]["password"]}
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_logout_user(client):
    """Test user logout"""
    # Register user
    client.post("/auth/register", json=TEST_USERS[0])

    # Login to get token
    login_data = {"username": TEST_USERS[0]["email"], "password": TEST_USERS[0]["password"]}
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Logout with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT or response.status_code == status.HTTP_200_OK


def test_register_multiple_users(client):
    """Test registering multiple users"""
    for user_data in TEST_USERS:
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["last_name"] == user_data["last_name"]


def test_login_multiple_users(client):
    """Test logging in with multiple users"""
    # Register multiple users
    for user_data in TEST_USERS:
        client.post("/auth/register", json=user_data)

    # Login with each user
    for user_data in TEST_USERS:
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
