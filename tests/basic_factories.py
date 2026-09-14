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


def category_data(name="Testkategori"):
    return {"name": name}


def song_data(category_id, **kwargs):
    data = {
        "title": "Testsång",
        "author": "Testförfattare",
        "melody": "Testmelodi",
        "content": "Testsångtext",
        "category_id": category_id,
    }
    return {**data, **kwargs}


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
        "start_time": (now - datetime.timedelta(days=1)).isoformat(),
        "description_sv": "Beskrivning",
        "description_en": "Description",
        "visible": True,
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


def create_candidation(client, sub_election_id: int, post_id: int, token=None, user_id: int | None = None):
    """Helper to POST /candidate/{election_id}?post_id=...&user_id=..."""
    headers = auth_headers(token) if token else {}
    url = f"/candidate/{sub_election_id}?post_id={post_id}"
    if user_id is not None:
        url += f"&user_id={user_id}"
    return client.post(url, headers=headers)


def sub_election_data_factory(**kwargs):
    """Factory for creating sub-election payloads with sensible default times."""
    now = datetime.datetime.now(timezone.utc)
    default_data = {
        "title_sv": "Val av poster",
        "title_en": "Election of Posts",
        "end_time": (now + datetime.timedelta(days=1)).isoformat(),
    }
    return {**default_data, **kwargs}


def create_sub_election(client, election_id, token=None, **kwargs):
    """Helper to POST /sub-election with optional token and payload overrides."""
    data = sub_election_data_factory(election_id=election_id, **kwargs)
    headers = auth_headers(token) if token else {}
    return client.post("/sub-election/", json=data, headers=headers)


def patch_sub_election(client, sub_election_id, token=None, **kwargs):
    """Helper to PATCH /sub-election/{id} with optional token and payload overrides."""
    data = sub_election_data_factory(**kwargs)
    headers = auth_headers(token) if token else {}
    return client.patch(f"/sub-election/{sub_election_id}", json=data, headers=headers)


def event_data_factory(**kwargs):
    """Factory for creating event payloads with sensible default times."""
    now = datetime.datetime.now(timezone.utc)
    default_data = {
        "starts_at": (now + datetime.timedelta(days=7)).isoformat(),
        "ends_at": (now + datetime.timedelta(days=7, hours=3)).isoformat(),
        "signup_start": (now - datetime.timedelta(days=1)).isoformat(),
        "signup_end": (now + datetime.timedelta(days=6)).isoformat(),
        "title_sv": "Testevenemang",
        "title_en": "Test Event",
        "description_sv": "Svensk beskrivning",
        "description_en": "English description",
        "location": "Kårhuset",
        "max_event_users": 0,
        "priorities": [],
        "all_day": False,
        "recurring": False,
        "food": False,
        "closed": False,
        "can_signup": True,
        "drink_package": False,
        "is_nollning_event": False,
        "mentor_group_types": ["Mentor", "Mission", "Default", "Committee"],
        "allow_other_mentors": False,
        "alcohol_event_type": "None",
        "dress_code": "Ovve",
        "price": 0,
        "dot": "None",
        "lottery": False,
    }
    return {**default_data, **kwargs}


def add_group_to_current_nollning(db_session, group):
    """Put a group in this year's nollning (created if missing). Returns the group."""

    return add_group_to_nollning(db_session, group, datetime.datetime.now(timezone.utc).year)


def add_group_to_nollning(db_session, group, year):
    """Put a group in specified year's nollning (created if missing). Returns the group."""

    from db_models.nollning_model import Nollning_DB
    from db_models.nollning_group_model import NollningGroup_DB

    nollning = db_session.query(Nollning_DB).filter_by(year=year).one_or_none()
    if nollning is None:
        nollning = Nollning_DB(name=f"Nollning {year}", description="Test nollning", year=year)
        db_session.add(nollning)
        db_session.commit()

    db_session.add(NollningGroup_DB(nollning_id=nollning.id, group_id=group.id))
    db_session.commit()

    return group


def add_user_to_group(db_session, user, name, group_type, group_user_type="Mentee"):
    """Create a group of a given type and put the user in it. Returns the group."""
    from db_models.group_model import Group_DB
    from db_models.group_user_model import GroupUser_DB

    group = Group_DB(name=name, group_type=group_type)
    db_session.add(group)
    db_session.commit()

    group_user = GroupUser_DB(
        user=user, user_id=user.id, group=group, group_id=group.id, group_user_type=group_user_type
    )
    db_session.add(group_user)
    db_session.commit()

    return group
