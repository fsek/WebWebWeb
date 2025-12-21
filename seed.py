import datetime
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db_models.cafe_shift_model import CafeShift_DB
from db_models.ad_model import BookAd_DB
from db_models.council_model import Council_DB
from db_models.election_model import Election_DB
from db_models.event_model import Event_DB
from db_models.news_model import News_DB
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from api_schemas.user_schemas import UserCreate
from db_models.song_category_model import SongCategory_DB
from db_models.song_model import Song_DB
from db_models.user_model import User_DB
from db_models.document_model import Document_DB
from pydantic_extra_types.phone_numbers import PhoneNumber
from db_models.sub_election_model import SubElection_DB
from db_models.election_post_model import ElectionPost_DB


def seed_users(db: Session, app: FastAPI):
    # This one seeds by actually calling user register route. Other create models directly
    client = TestClient(app)
    boss = UserCreate(
        email="boss@fsektionen.se",
        first_name="Boss",
        last_name="AllaPostersson",
        password="dabdab69",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user = UserCreate(
        email="user@fsektionen.se",
        first_name="User",
        last_name="Userström",
        password="dabdab69",
        telephone_number=PhoneNumber("+46706427444"),
    )
    user2 = UserCreate(
        email="user2@fsektionen.se",
        first_name="User2",
        last_name="Userström2",
        password="dabdab69",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user3 = UserCreate(
        email="user3@fsektionen.se",
        first_name="User3",
        last_name="Userström3",
        password="dabdab69",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user4 = UserCreate(
        email="user4@fsektionen.se",
        first_name="User4",
        last_name="Userström4",
        password="dabdab69",
        telephone_number=PhoneNumber("+46760187158"),
    )

    boss_response = client.post("/auth/register", json=boss.model_dump())
    assert boss_response.status_code == 201
    response = client.post("/auth/register", json=user.model_dump())
    assert response.status_code == 201
    user2_response = client.post("/auth/register", json=user2.model_dump())
    assert user2_response.status_code == 201
    user3_response = client.post("/auth/register", json=user3.model_dump())
    assert user3_response.status_code == 201
    user4_response = client.post("/auth/register", json=user4.model_dump())
    assert user4_response.status_code == 201

    client.close()
    boss_id = boss_response.json()["id"]
    user_id = response.json()["id"]
    user2_id = user2_response.json()["id"]
    user3_id = user3_response.json()["id"]
    user4_id = user4_response.json()["id"]

    # now fetch the created users and set is_verified to True
    boss = db.query(User_DB).filter_by(id=boss_id).one()
    user = db.query(User_DB).filter_by(id=user_id).one()
    user2 = db.query(User_DB).filter_by(id=user2_id).one()
    user3 = db.query(User_DB).filter_by(id=user3_id).one()
    user4 = db.query(User_DB).filter_by(id=user4_id).one()

    boss.is_verified = True
    user.is_verified = True
    boss.is_member = True
    user2.is_verified = True
    user3.is_verified = True
    user4.is_verified = True
    boss.is_member = True
    user.is_member = True
    user2.is_member = True
    user3.is_member = True
    user4.is_member = True

    db.commit()
    return boss, user


def seed_cafe_shifts(db: Session, user: User_DB):
    starts_at = datetime.datetime.now(datetime.UTC)
    ends_at = starts_at + datetime.timedelta(hours=1)
    shift = CafeShift_DB(starts_at=starts_at, ends_at=ends_at)
    shift.user = user
    shift.user_id = user.id
    db.add(shift)
    db.commit()
    return shift


def seed_councils(db: Session):
    councils = [
        Council_DB(
            name_sv="Kodmästeriet",
            description_sv="bra beskrivning",
            name_en="The Code Masters",
            description_en="a better description",
        ),
        Council_DB(
            name_sv="Sanningsministeriet",
            description_sv="bättre beskrivning",
            name_en="The Ministry of Truth",
            description_en="an even better description",
        ),
    ]
    db.add_all(councils)
    db.commit()

    return councils


def seed_posts(db: Session, some_councils: list[Council_DB]):
    posts = [
        Post_DB(
            name_sv="Buggmästare",
            name_en="Bugmaster",
            council_id=some_councils[0].id,
            description_sv="buggmästare",
            description_en="bugmaster",
            email="buggmastare@fsektionen.se",
            elected_at_semester="HT and VT",
            elected_by="Board",
        ),
        Post_DB(
            name_sv="Lallare",
            name_en="Laller",
            council_id=some_councils[0].id,
            description_sv="lallare",
            description_en="laller",
            email="lallare@fsektionen.se",
            elected_at_semester="HT and VT",
            elected_by="Guild",
        ),
        Post_DB(
            name_sv="Mytoman",
            name_en="Liar",
            council_id=some_councils[1].id,
            description_sv="mytoman",
            description_en="liar",
            email="mytoman@fsektionen.se",
            elected_at_semester="VT",
            elected_by="Guild",
        ),
    ]
    db.add_all(posts)
    db.commit()

    return posts


def seed_post_users(db: Session, boss: User_DB, user: User_DB, posts: list[Post_DB]):
    # Give posts to users
    boss.posts = posts
    user.posts.append(posts[0])
    db.commit()


# Wrapper class for Permission_DB that includes the target posts
class Permission(Permission_DB):
    def __init__(self, action=None, target=None, posts: list[str] = []):
        super().__init__(action=action, target=target)
        self.posts = posts

    def degenerate(self) -> super:
        return Permission_DB(action=self.action, target=self.target)


def seed_permissions(db: Session, posts: list[Post_DB]):

    permissions = [
        Permission(action="manage", target="Permission", posts=["Buggmästare"]),
        Permission(action="view", target="User", posts=["Buggmästare"]),
        Permission(action="manage", target="Event", posts=["Lallare"]),
        Permission(action="manage", target="Post", posts=["Buggmästare"]),
        Permission(action="manage", target="News", posts=["Lallare"]),
        Permission(action="manage", target="Song", posts=["Buggmästare"]),
        Permission(action="manage", target="Gallery", posts=["Buggmästare"]),
        Permission(action="manage", target="Ads", posts=["Buggmästare"]),
        Permission(action="manage", target="Car", posts=["Buggmästare"]),
        Permission(action="manage", target="Election", posts=["Buggmästare"]),
        Permission(action="manage", target="Cafe", posts=["Lallare"]),
        Permission(action="manage", target="Groups", posts=["Buggmästare"]),
        Permission(action="manage", target="Tags", posts=["Buggmästare"]),
        Permission(action="manage", target="AdventureMissions", posts=["Buggmästare"]),
        Permission(action="manage", target="Nollning", posts=["Buggmästare"]),
        Permission(action="view", target="Nollning", posts=["Buggmästare"]),
        Permission(action="manage", target="Council", posts=["Buggmästare"]),
        Permission(action="view", target="Council", posts=["Buggmästare"]),
        Permission(action="manage", target="User", posts=["Buggmästare"]),
        Permission(action="manage", target="RoomBookings", posts=["Buggmästare"]),
        Permission(action="view", target="RoomBookings", posts=["Buggmästare"]),
        Permission(action="manage", target="UserDoorAccess", posts=["Buggmästare"]),
        Permission(action="view", target="UserDoorAccess", posts=["Buggmästare"]),
        Permission(action="manage", target="Document", posts=["Buggmästare"]),
        Permission(action="view", target="Document", posts=["Buggmästare"]),
        Permission(action="manage", target="Moosegame", posts=["Buggmästare"]),
        Permission(action="manage", target="UserPost", posts=["Buggmästare"]),
        Permission(action="view", target="GuildMeeting", posts=["Buggmästare"]),
        Permission(action="manage", target="GuildMeeting", posts=["Buggmästare"]),
        Permission(action="manage", target="Fruit", posts=["Buggmästare"]),
    ]

    [
        [post.permissions.append(perm.degenerate()) for perm in permissions if post.name_sv in perm.posts]
        for post in posts
    ]

    db.commit()


def seed_events(db: Session, one_council: Council_DB):
    starts_at = datetime.datetime.now(datetime.UTC)
    signup_start = starts_at + datetime.timedelta(hours=1)
    signup_end = signup_start + datetime.timedelta(hours=1)
    ends_at = signup_end + datetime.timedelta(hours=1)
    event = Event_DB(
        council_id=one_council.id,
        starts_at=starts_at,
        ends_at=ends_at,
        description_en="Dis gun be litty",
        description_sv="Det blir fett gäähda",
        title_en="Phat party",
        title_sv="Loyde gähdda",
        signup_start=signup_start,
        signup_end=signup_end,
        location="Mattehuset",
        dress_code="vad du vill",
        price=123,
        alcohol_event_type="Alcohol",
        dot="Double",
        lottery=False,
    )
    db.add(event)
    db.commit()
    return event


def seed_news(db: Session, user: User_DB):
    news = [
        News_DB(
            title_sv="Min första nyhet :))",
            title_en="My first news :smilyface:",
            content_sv="Oj här var det ju en massa spännande saker man kunde läsa!",
            content_en="Whoops here there was a lot of content to read!",
            author_id=user.id,
        ),
        News_DB(
            title_sv="En annan nyhet",
            title_en="Another news",
            content_sv="Lite mer content",
            content_en="A bit more content",
            author_id=user.id,
        ),
    ]

    for i in range(1, 100):
        news.append(
            News_DB(
                title_sv="test",
                title_en="Another news",
                content_sv="Lite mer content",
                content_en="A bit more content",
                author_id=user.id,
            )
        )

    db.add_all(news)
    db.commit()


def seed_songs_and_song_category(db: Session):
    category = SongCategory_DB(name="Lofi hip hop - beats to study/relax to")
    db.add(category)

    song = Song_DB(
        title="Never Gonna Give You Up",
        author="rick astley n77",
        content="Blah,blah,blah",
        category_id=1,
    )

    db.add(song)
    db.commit()
    return


def seed_ads(db: Session):
    users = db.query(User_DB).all()

    ad = BookAd_DB(title="Endim", course="FMNAF05", author="Jonas", price=50, selling=True, user_id=users[0].id)
    db.add(ad)
    ad = BookAd_DB(title="Flerdim", course="FMNAF25", author="Jonas", price=190, selling=True, user_id=users[0].id)
    db.add(ad)
    ad = BookAd_DB(title="Linalg", course="FMNAF35", author="Jonas", price=920, selling=True, user_id=users[2].id)
    db.add(ad)
    ad = BookAd_DB(title="Våglära", course="VAG01", author="Tjalle", price=9430, selling=False, user_id=users[1].id)
    db.add(ad)
    ad = BookAd_DB(title="Java", course="JA25", author="Patrik", price=50, selling=True, user_id=users[1].id)
    db.add(ad)
    ad = BookAd_DB(title="EffektivC", course="EC10", author="Skeppstedt", price=90, selling=True, user_id=users[0].id)
    db.add(ad)
    ad = BookAd_DB(title="Matstat", course="MATS100", author="Tant", price=670, selling=False, user_id=users[1].id)
    db.add(ad)
    ad = BookAd_DB(title="Termo", course="VARM20", author="Thomas", price=90, selling=True, user_id=users[1].id)
    db.add(ad)
    ad = BookAd_DB(title="Kemi", course="BOOM12", author="Bengt", price=10, selling=False, user_id=users[3].id)
    db.add(ad)
    ad = BookAd_DB(title="Endim", course="FMNAF05", author="Jonas", price=1, selling=True, user_id=users[4].id)
    db.add(ad)
    ad = BookAd_DB(title="Endim", course="FMNAF05", author="Jonas", price=10, selling=True, user_id=users[2].id)
    db.add(ad)
    db.commit()


def seed_election(db: Session):
    starts_at = datetime.datetime.now(datetime.UTC)
    signup_start = starts_at + datetime.timedelta(hours=24)
    signup_end = signup_start + datetime.timedelta(hours=24)
    elections = [
        Election_DB(
            title_sv="bajsval1928",
            title_en="poopelection1928",
            start_time=signup_start,
            description_sv="Snälla bajs",
            description_en="Please work",
        ),
        Election_DB(
            title_sv="360noscope",
            title_en="360noscope but in english",
            start_time=signup_start,
            description_sv="lol get wrekt (in swedish)",
            description_en="lol get wrecked but in english",
        ),
    ]
    db.add_all(elections)  # Use add_all to add multiple instances
    db.commit()
    db.refresh(elections[0])
    db.refresh(elections[1])

    # Election posts
    election_posts = [
        ElectionPost_DB(
            post_id=1,
        ),
        ElectionPost_DB(
            post_id=2,
        ),
        ElectionPost_DB(
            post_id=3,
        ),
    ]

    # Now add subelections
    sub_election_1 = SubElection_DB(
        election_id=elections[0].election_id,
        title_sv="Alla coola poster",
        title_en="All the cool posts",
        end_time=signup_end,
        election_posts=[election_posts[0], election_posts[1]],
    )

    sub_election_2 = SubElection_DB(
        election_id=elections[1].election_id,
        title_sv="Bara dåliga poster",
        title_en="Only the lame posts",
        end_time=signup_end,
        election_posts=[election_posts[2]],
    )

    db.add(sub_election_1)
    db.add(sub_election_2)
    db.commit()


def seed_documents(db: Session):
    # Start by removing all the old documents

    base_path = os.getenv("DOCUMENT_BASE_PATH")

    if base_path is None:
        base_path = "/workspaces/WebWebWeb/test-assets/documents"

    # directories are kept as is
    for root, dirs, files in os.walk(base_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))

    # Now create the PDF
    from reportlab.pdfgen import canvas

    pdf_file = os.path.join(base_path, "simple_test_document.pdf")

    # Create a simple PDF
    c = canvas.Canvas(pdf_file)
    c.drawString(100, 750, "Hello, World!")
    c.save()

    # Now create the document object in the backend
    document = Document_DB(
        title="Simple Test Document",
        file_name="simple_test_document.pdf",
        category="cool category",
        author_id=1,
    )
    db.add(document)
    db.commit()


def seed_if_empty(app: FastAPI, db: Session):
    # If there's no user, assumed DB is empty and seed it.
    if db.query(User_DB).count() > 0:
        return

    print("Time to seed.")

    councils = seed_councils(db)

    posts = seed_posts(db, councils)

    seed_permissions(db, posts)

    boss, user = seed_users(db, app)

    seed_cafe_shifts(db, user)

    seed_post_users(db, boss, user, posts)

    seed_events(db, councils[1])

    seed_news(db, boss)

    seed_songs_and_song_category(db)

    seed_ads(db)

    seed_election(db)

    seed_documents(db)

    print("Done seeding!")
