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
    post = Post_DB(
        name_sv="AdminPostSV",
        name_en="AdminPost",
        description_en="AdminDescriptionEn",
        description_sv="AdminDescriptionSv",
        council_id=council.id,
        elected_user_recommended_limit=1,
        elected_user_max_limit=2,
    )
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
        Permission_DB(action="view", target="Election"),
        Permission_DB(action="manage", target="Election"),
        Permission_DB(action="manage", target="Cafe"),
        Permission_DB(action="manage", target="Groups"),
        Permission_DB(action="view", target="Groups"),
        Permission_DB(action="manage", target="UserDoorAccess"),
        Permission_DB(action="view", target="UserDoorAccess"),
        Permission_DB(action="manage", target="AdventureMissions"),
        Permission_DB(action="manage", target="Nollning"),
        Permission_DB(action="view", target="Nollning"),
        Permission_DB(action="manage", target="Tags"),
        Permission_DB(action="manage", target="Council"),
        Permission_DB(action="view", target="Council"),
        Permission_DB(action="manage", target="User"),
        Permission_DB(action="manage", target="RoomBookings"),
        Permission_DB(action="view", target="UserPost"),
        Permission_DB(action="manage", target="UserPost"),
        Permission_DB(action="view", target="RoomBookings"),
        Permission_DB(action="manage", target="RoomBookings"),
        Permission_DB(action="view", target="Document"),
        Permission_DB(action="manage", target="Document"),
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

    post = Post_DB(
        name_en="rkngkr", name_sv="kejfk", description_en="jrv", description_sv="rekngvrjn", council_id=council.id
    )
    db_session.add(post)
    db_session.commit()

    membered_user.posts.append(post)
    db_session.commit()

    return council.id


@pytest.fixture()
def member_post(db_session, member_council_id):
    """Return the post DB object just created for the member council."""
    from db_models.post_model import Post_DB

    post = db_session.query(Post_DB).filter_by(council_id=member_council_id).first()
    assert post is not None, "No post found for the member council"
    return post


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


@pytest.fixture()
def example_file():
    """Creates a test pdf file and returns it as a file-like object"""
    from reportlab.pdfgen import canvas

    pdf_file = "simple_test_document.pdf"

    # Create a simple PDF
    c = canvas.Canvas(pdf_file)
    c.drawString(100, 750, "Hello, World!")
    c.save()
    # Return as (filename, file_object, content_type)
    f = open(pdf_file, "rb")
    return (pdf_file, f, "application/pdf")


@pytest.fixture()
def open_election(db_session):
    """Create and return an election that is currently open."""
    from datetime import datetime, timedelta
    from db_models.election_model import Election_DB

    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(days=1)).isoformat()

    election = Election_DB(
        title_sv="Öppen val",
        title_en="Open Election",
        description_sv="Ett val som är öppet",
        description_en="An election that is open",
        start_time=start_time,
        visible=True,
    )
    db_session.add(election)
    db_session.commit()
    db_session.refresh(election)
    return election


@pytest.fixture()
def open_sub_election(db_session, open_election, admin_post, member_post):
    """Create and return a sub-election that is currently open with two posts."""
    from db_models.sub_election_model import SubElection_DB
    from db_models.election_post_model import ElectionPost_DB
    from datetime import datetime, timedelta

    now = datetime.now(timezone.utc)
    end_time = (now + timedelta(days=1)).isoformat()

    admin_election_post = ElectionPost_DB(post_id=admin_post.id)
    member_election_post = ElectionPost_DB(post_id=member_post.id)

    sub_election = SubElection_DB(
        election_id=open_election.election_id,
        title_sv="Öppen delval",
        title_en="Open Sub Election",
        end_time=end_time,
        election_posts=[admin_election_post, member_election_post],
    )
    db_session.add(sub_election)
    db_session.commit()
    db_session.refresh(sub_election)
    return sub_election
