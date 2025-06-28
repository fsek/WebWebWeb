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

    council = Council_DB(name="AdminCouncil", description="Council for admins")
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

    user_data = user_data_factory(email="admin@example.com", first_name="Admin", last_name="User")
    user_in_db = create_membered_user(client, db_session, **user_data)

    # Assign admin post
    user_in_db.posts.append(admin_post)
    db_session.commit()

    user_in_db = db_session.query(User_DB).filter_by(id=user_in_db.id).one()
    return user_in_db
