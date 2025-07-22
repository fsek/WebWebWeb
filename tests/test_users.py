# type: ignore
import pytest
from sqlalchemy import text
from fastapi import status
from .basic_factories import user_data_factory, create_membered_user


def test_register_user(client, user1_data):
    """Test user registration with valid data"""
    response = client.post("/auth/register", json=user1_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
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
    response = client.delete("/auth/logout", headers=headers)
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


def test_admin_post_fixture(admin_post, db_session):
    """Test that the admin_post fixture creates a post with correct attributes."""
    from db_models.post_model import Post_DB

    post = db_session.query(Post_DB).filter_by(id=admin_post.id).one()
    assert post.name == "AdminPost"
    assert post.council.name == "AdminCouncil"


def test_admin_user_fixture(admin_user, db_session):
    """Test that the admin_user fixture creates a user with admin post and is_member True."""
    from db_models.user_model import User_DB

    user = db_session.query(User_DB).filter_by(email="admin@example.com").one()
    assert user.is_member is True
    assert user.is_verified is True
    assert any(post.name == "AdminPost" for post in user.posts)


def test_membered_user_factory(client, db_session):
    """Test that the membered_user factory creates a user with is_member True."""
    from db_models.user_model import User_DB

    create_membered_user(client, db_session, **user_data_factory(email="member@example.com"))

    user = db_session.query(User_DB).filter_by(email="member@example.com").one()
    assert user.is_member is True
    assert user.is_verified is True
