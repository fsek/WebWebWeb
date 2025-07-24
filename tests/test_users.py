# type: ignore
import pytest
from sqlalchemy import text
from fastapi import status
from .basic_factories import user_data_factory, create_membered_user, auth_headers


def test_register_user(client, user1_data):
    """Test user registration with valid data"""
    response = client.post("/auth/register", json=user1_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    # assert data["program"] == user1_data["program"]
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


def test_change_password_user(client, registered_user):
    """Test changing password for a registered user"""
    # Registration happens in the fixture, so we can directly test password change
    login_data = {"username": registered_user["email"], "password": registered_user["password"]}
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    new_password = "new_secure_password69"
    change_password_data = {
        "username": registered_user["email"],
        "password": registered_user["password"],
        "new_password": new_password,
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    response = client.patch("/auth/update-password", data=change_password_data, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify that session is invalidated after password change
    # Attempt to access a protected route with the old session token
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Verify that the old password no longer works
    login_data["password"] = registered_user["password"]
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verify that the new password works
    login_data["password"] = new_password
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK


def test_change_email_user(client, registered_user, db_session):
    """Test changing email for a registered user"""
    # Registration happens in the fixture, so we can directly test email change
    login_data = {"username": registered_user["email"], "password": registered_user["password"]}
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    new_email = "hilbert_himself@fsektionen.se"  # New email for the user
    change_email_data = {
        "username": registered_user["email"],
        "password": registered_user["password"],
        "new_email": new_email,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    response = client.patch("/auth/update-email", data=change_email_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # Verify that the old email no longer works
    login_data["username"] = registered_user["email"]
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Verify that the new email works
    login_data["username"] = new_email
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    # Verify that the user's email is no longer verified
    from db_models.user_model import User_DB

    db_user = db_session.query(User_DB).filter_by(email=new_email).one()
    assert db_user.email == new_email
    assert db_user.is_verified is False


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
    assert post.council.name_sv == "AdminCouncilSV"


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


def test_change_phone_num(membered_user, client, db_session, member_token):
    """Test changing phone number for a membered user."""
    from db_models.user_model import User_DB
    import re

    # Ensure the user has a phone number
    assert membered_user.telephone_number is not None

    new_phone_number = "+46701234567"
    response = client.patch(
        "/users/update/me",
        json={"telephone_number": new_phone_number},
        headers=auth_headers(member_token),
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify the phone number was updated
    updated_user = db_session.query(User_DB).filter_by(id=membered_user.id).one()

    def only_digits(s):
        return re.sub(r"\D", "", s)

    assert only_digits(updated_user.telephone_number) == only_digits(new_phone_number)


def test_change_phone_num_invalid_format(membered_user, client, db_session, member_token):
    """Test changing phone number with invalid format."""
    from db_models.user_model import User_DB

    invalid_phone_number = "12345"  # Invalid format
    response = client.patch(
        "/users/update/me",
        json={"telephone_number": invalid_phone_number},
        headers=auth_headers(member_token),
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Verify the phone number was not updated
    updated_user = db_session.query(User_DB).filter_by(id=membered_user.id).one()
    assert updated_user.telephone_number == membered_user.telephone_number
