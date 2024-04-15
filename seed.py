import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db_models.ad_model import BookAd_DB
from db_models.council_model import Council_DB
from db_models.event_model import Event_DB
from db_models.news_model import News_DB
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from api_schemas.user_schemas import UserCreate
from db_models.song_category_model import SongCategory_DB
from db_models.song_model import Song_DB
from db_models.user_model import User_DB
from pydantic_extra_types.phone_numbers import PhoneNumber


def seed_users(db: Session, app: FastAPI):
    # This one seeds by actually calling user register route. Other create models directly
    client = TestClient(app)
    boss = UserCreate(
        email="boss@fsektionen.se",
        first_name="Boss",
        last_name="AllaPostersson",
        password="dabdab",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user = UserCreate(
        email="user@fsektionen.se",
        first_name="User",
        last_name="Userström",
        password="dabdab",
        telephone_number=PhoneNumber("+46706427444"),
    )
    user2 = UserCreate(
        email="user2@fsektionen.se",
        firstname="User2",
        lastname="Userström2",
        password="dabdab",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user3 = UserCreate(
        email="user3@fsektionen.se",
        firstname="User3",
        lastname="Userström3",
        password="dabdab",
        telephone_number=PhoneNumber("+46760187158"),
    )
    user4 = UserCreate(
        email="user4@fsektionen.se",
        firstname="User4",
        lastname="Userström4",
        password="dabdab",
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
    user2.is_verified = True
    user3.is_verified = True
    user4.is_verified = True
    
    db.commit()
    return boss, user


def seed_councils(db: Session):
    councils = [Council_DB(name="Kodmästeriet"), Council_DB(name="Sanningsministeriet")]
    db.add_all(councils)
    db.commit()

    return councils


def seed_posts(db: Session, some_councils: list[Council_DB]):
    posts = [
        Post_DB(name="Buggmästare", council_id=some_councils[0].id),
        Post_DB(name="Lallare", council_id=some_councils[0].id),
        Post_DB(name="Mytoman", council_id=some_councils[1].id),
    ]
    db.add_all(posts)
    db.commit()

    return posts


def seed_post_users(db: Session, boss: User_DB, user: User_DB, posts: list[Post_DB]):
    # Give posts to users
    boss.posts = posts
    user.posts.append(posts[0])
    db.commit()


def seed_permissions(db: Session, posts: list[Post_DB]):
    perm1 = Permission_DB(action="manage", target="Permission")
    perm2 = Permission_DB(action="view", target="User")
    perm3 = Permission_DB(action="manage", target="Event")
    perm4 = Permission_DB(action="manage", target="Post")
    perm5 = Permission_DB(action="manage", target="News")
    perm6 = Permission_DB(action="manage", target="Song")
    perm7 = Permission_DB(action="manage", target="Ads")
    posts[0].permissions.append(perm1)
    posts[0].permissions.append(perm2)
    posts[1].permissions.append(perm3)
    posts[0].permissions.append(perm4)
    posts[1].permissions.append(perm5)
    posts[0].permissions.append(perm6)
    posts[0].permissions.append(perm7)
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

def seed_ads(db:Session):
    users = db.query(User_DB).all()
    
    ad = BookAd_DB(title = "Endim", course = "FMNAF05", author = "Jonas", price = 50, selling = True, user_id = users[0].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Flerdim", course = "FMNAF25", author = "Jonas", price = 190, selling = True, user_id = users[0].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Linalg", course = "FMNAF35", author = "Jonas", price = 920, selling = True,user_id = users[2].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Våglära", course = "VAG01", author = "Tjalle", price = 9430, selling = False, user_id = users[1].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Java", course = "JA25", author = "Patrik", price = 50, selling = True, user_id = users[1].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "EffektivC", course = "EC10", author = "Skeppstedt", price = 90, selling = True, user_id = users[0].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Matstat", course = "MATS100", author = "Tant", price = 670, selling = False, user_id = users[1].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Termo", course = "VARM20", author = "Thomas", price = 90, selling = True, user_id = users[1].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Kemi", course = "BOOM12", author = "Bengt", price = 10, selling = False, user_id = users[3].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Endim", course = "FMNAF05", author = "Jonas", price = 1, selling = True, user_id = users[4].id)
    db.add(ad)
    db.commit()
    ad = BookAd_DB(title = "Endim", course = "FMNAF05", author = "Jonas", price = 10, selling = True, user_id = users[2].id)
    db.add(ad)
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

    seed_post_users(db, boss, user, posts)

    seed_events(db, councils[1])

    seed_news(db, boss)
    seed_songs_and_song_category(db)

    seed_songs_and_song_category(db)
    
    seed_ads(db)

    print("Done seeding!")
