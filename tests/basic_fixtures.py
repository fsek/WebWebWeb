# type: ignore
import pytest
from .basic_factories import *


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


@pytest.fixture
def admin_post(db_session):
    """Create and return an admin post."""
    from db_models.post_model import Post_DB
    from db_models.council_model import Council_DB
    from db_models.permission_model import Permission_DB

    council = Council_DB(
        name_sv="AdminCouncilSV",
        description_sv="Svensk beskrivning för admins",
        name_en="AdminCouncilEN",
        description_en="English description for admins",
    )
    db_session.add(council)
    db_session.commit()
    post = Post_DB(name="AdminPost", council_id=council.id)
    db_session.add(post)
    db_session.commit()

    # Assign all permissions which we have in seed.py to the admin post
    permissions = [
        Permission_DB(action="manage", target="Permission"),
        Permission_DB(action="view", target="User"),
        Permission_DB(action="manage", target="Event"),
        Permission_DB(action="manage", target="Post"),
        Permission_DB(action="manage", target="News"),
        Permission_DB(action="manage", target="Song"),
        Permission_DB(action="manage", target="Gallery"),
        Permission_DB(action="manage", target="Ads"),
        Permission_DB(action="manage", target="Car"),
        Permission_DB(action="manage", target="Election"),
        Permission_DB(action="manage", target="Cafe"),
        Permission_DB(action="manage", target="Groups"),
        Permission_DB(action="view", target="Groups"),
        Permission_DB(action="manage", target="UserDoorAccess"),
        Permission_DB(action="view", target="UserDoorAccess"),
        Permission_DB(action="manage", target="Adventure Missions"),
        Permission_DB(action="manage", target="Nollning"),
        Permission_DB(action="view", target="Nollning"),
        Permission_DB(action="manage", target="Tags"),
        Permission_DB(action="manage", target="Council"),
        Permission_DB(action="view", target="Council"),
        Permission_DB(action="manage", target="User"),
    ]
    post.permissions.extend(permissions)
    db_session.commit()

    return post


@pytest.fixture
def admin_user(client, db_session, admin_post):
    """Create and return a full admin user with the admin post and permissions."""
    from db_models.user_model import User_DB

    user_data = user_data_factory(
        email="admin@example.com", first_name="Admin", last_name="User", password="Password123"
    )
    user_in_db = create_membered_user(client, db_session, **user_data)

    # Assign admin post
    user_in_db.posts.append(admin_post)
    db_session.commit()

    return user_in_db


@pytest.fixture
def membered_user(client, db_session):
    """Create and return a user who is a member and verified."""
    user_data = user_data_factory(
        email="member@example.com", first_name="Member", last_name="User", password="Password123"
    )
    user = create_membered_user(client, db_session, **user_data)

    return user


@pytest.fixture()
def admin_token(client, admin_user):
    """Create an admin user and return its access token."""

    resp = client.post("/auth/login", data={"username": "admin@example.com", "password": "Password123"})
    return resp.json()["access_token"]


@pytest.fixture()
def member_token(client, membered_user):
    """Create a member user and return its access token."""

    resp = client.post("/auth/login", data={"username": "member@example.com", "password": "Password123"})
    return resp.json()["access_token"]


@pytest.fixture()
def member_council_id(client, db_session, membered_user):
    """Create a useless council with a member user and return its ID."""
    from db_models.council_model import Council_DB
    from db_models.post_model import Post_DB

    council = Council_DB(
        name_sv="MemberCouncilSV",
        description_sv="Svensk beskrivning för medlemmar",
        name_en="MemberCouncilEN",
        description_en="English description for members",
    )
    db_session.add(council)
    db_session.commit()

    post = Post_DB(name="MemberPost", council_id=council.id)
    db_session.add(post)
    db_session.commit()

    membered_user.posts.append(post)
    db_session.commit()

    return council.id


@pytest.fixture()
def admin_council_id(db_session, admin_user):
    """Create a council with an admin user and return its ID."""

    # Extract the admin council ID from the admin user, everything created via admin_user fixture
    council_id = admin_user.posts[0].council_id

    return council_id


@pytest.fixture()
def non_membered_user(client, db_session):
    """Create and return a user who is not a member."""
    user_data = user_data_factory(
        email="non-member@example.com", first_name="NonMember", last_name="User", password="Password123"
    )
    user = create_membered_user(client, db_session, **user_data)
    # Ensure the user is not a member
    user.is_member = False
    user.is_verified = True  # Still verified
    db_session.commit()
    return user


@pytest.fixture()
def non_member_token(client, non_membered_user):
    """Create a non-member user and return its access token."""
    resp = client.post("/auth/login", data={"username": "non-member@example.com", "password": "Password123"})
    return resp.json()["access_token"]
