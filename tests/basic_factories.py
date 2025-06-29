# type: ignore


def user_data_factory(**kwargs):
    default_data = {
        "email": "test@example.com",
        "password": "Password123",
        "first_name": "Test",
        "last_name": "User",
        "start_year": 2023,
        "program": "F",
        "telephone_number": "+46701234567",
    }
    """Factory function to complete user data dicts."""
    return {**default_data, **kwargs}


def create_membered_user(client, db_session, **kwargs):
    """Create and return a user who is a member and verified."""
    from db_models.user_model import User_DB

    defaults = {
        "email": "member@example.com",
        "first_name": "Member",
        "last_name": "User",
    }

    user_data = user_data_factory(**{**defaults, **kwargs})  # It just works (removes duplicates)

    # Register the user
    register_response = client.post("/auth/register", json=user_data)

    assert (
        register_response.status_code == 201
    ), f"Expected status code 201, got {register_response.status_code} with response: {register_response.text}"

    user_id = register_response.json()["id"]

    # Make user member and verified
    user_in_db = db_session.query(User_DB).filter_by(id=user_id).one()
    user_in_db.is_member = True
    user_in_db.is_verified = True
    db_session.commit()
    return user_in_db
