# type: ignore
import datetime
from datetime import timezone


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


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def council_data_factory(**kwargs):
    """Factory for council create/update payloads."""
    default_data = {
        "name_sv": "Testutskott",
        "description_sv": "Test beskrivning",
        "name_en": "Test Council",
        "description_en": "Test description",
    }
    return {**default_data, **kwargs}


def create_council(client, token=None, **kwargs):
    """Helper to POST /councils/ with optional token and payload overrides."""
    data = council_data_factory(**kwargs)
    headers = auth_headers(token) if token else {}
    return client.post("/councils/", json=data, headers=headers)


def election_data_factory(**kwargs):
    """Factory for creating election payloads with sensible default times."""
    now = datetime.datetime.now(timezone.utc)
    default_data = {
        "title_sv": "Testval SV",
        "title_en": "Test Election EN",
        "start_time": (now + datetime.timedelta(days=1)).isoformat(),
        "end_time_guild_meeting": (now + datetime.timedelta(days=2)).isoformat(),
        "end_time_middle_meeting": None,
        "end_time_all": (now + datetime.timedelta(days=3)).isoformat(),
        "description_sv": "Beskrivning",
        "description_en": "Description",
        "post_ids": [],
    }
    return {**default_data, **kwargs}


def create_election(client, token=None, **kwargs):
    """Helper to POST /election with optional token and payload overrides."""
    data = election_data_factory(**kwargs)
    headers = auth_headers(token) if token else {}
    return client.post("/election", json=data, headers=headers)


def patch_election(client, election_id, token=None, **kwargs):
    """Helper to PATCH /election/{id} with optional token and payload overrides."""
    data = election_data_factory(**kwargs)
    headers = auth_headers(token) if token else {}
    return client.patch(f"/election/{election_id}", json=data, headers=headers)
