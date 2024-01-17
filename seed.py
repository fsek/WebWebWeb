import datetime
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db_models.council_model import Council_DB
from db_models.event_model import Event_DB
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from schemas.user_schemas import UserCreate
from db_models.user_model import User_DB

fake = Faker()


def seed_users(db: Session, app: FastAPI):
    # This one seeds by actually calling user register route. Other create models directly
    client = TestClient(app)

    boss = UserCreate(email="boss@fsektionen.se", firstname="Boss", lastname="AllaPostersson", password="dabdab")
    user = UserCreate(email="user@fsektionen.se", firstname="User", lastname="Userström", password="dabdab")

    boss_response = client.post("/auth/register", json=boss.model_dump())
    assert boss_response.status_code == 201
    response = client.post("/auth/register", json=user.model_dump())
    assert response.status_code == 201

    client.close()
    boss_id = boss_response.json()["id"]
    user_id = response.json()["id"]

    # now fetch the created users and set is_verified to True
    boss = db.query(User_DB).filter_by(id=boss_id).one()
    user = db.query(User_DB).filter_by(id=user_id).one()

    boss.is_verified = True
    user.is_verified = True

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
    posts[0].permissions.append(perm1)
    posts[0].permissions.append(perm2)
    posts[1].permissions.append(perm3)
    db.commit()


def seed_events(db: Session, one_council: Council_DB):
    start = datetime.datetime.now(datetime.timezone.utc)
    end = start + datetime.timedelta(hours=3)
    event = Event_DB(
        council_id=one_council.id,
        starts_at=start,
        ends_at=end,
        description_en="Dis gun be litty",
        description_sv="Det blir fett gäähda",
    )
    db.add(event)
    db.commit()
    return event


def seed_if_empty(app: FastAPI, db: Session):
    if db.query(User_DB).count() > 0:
        return

    print("Time to seed.")

    councils = seed_councils(db)

    posts = seed_posts(db, councils)

    seed_permissions(db, posts)

    boss, user = seed_users(db, app)

    seed_post_users(db, boss, user, posts)

    seed_events(db, councils[1])
