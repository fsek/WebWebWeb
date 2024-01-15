from datetime import datetime
from math import floor
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db_models.council_model import Council_DB
from db_models.event_model import Event_DB
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from db_models.post_permission_model import PostPermission_DB
from schemas.schemas import UserCreate
from db_models.user_model import User_DB

fake = Faker()


def seed_users(db: Session, app: FastAPI):
    # This one seeds by actually calling user register route. Other create models directly
    client = TestClient(app)
    admin = UserCreate(email="admin@fsektionen.se", firstname="Admin", lastname="Adminsson", password="dabdab")
    user = UserCreate(email="user@fsektionen.se", firstname="User", lastname="Userström", password="dabdab")

    admin_response = client.post("/auth/register", json=admin.model_dump())
    assert admin_response.status_code == 201
    response = client.post("/auth/register", json=user.model_dump())
    assert response.status_code == 201
    client.close()
    return admin_response.json(), response.json()


def seed_councils(db: Session):
    councils = [Council_DB(name="Kodmästeriet"), Council_DB(name="Sanningsministeriet")]
    db.add_all(councils)
    db.commit()

    return councils


def seed_posts(db: Session, one_council: Council_DB):
    posts = [
        Post_DB(name="Buggmästare", council_id=one_council.id),
        Post_DB(name="Mytoman", council_id=one_council.id),
        Post_DB(name="Lallare", council_id=one_council.id),
    ]
    db.add_all(posts)
    db.commit()

    return posts


def seed_post_users(db: Session, one_post: Post_DB):
    # Give a post to half of users
    users = db.query(User_DB).all()
    for u in users:
        u.posts.append(one_post)

    db.commit()


def seed_permissions(db: Session, one_post: Post_DB):
    perm = Permission_DB(action="read", target="A")
    one_post.permissions.append(perm)
    db.commit()


def seed_events(db: Session, one_council: Council_DB):
    event = Event_DB(
        council_id=one_council.id,
        starts_at=datetime.today(),
        ends_at=datetime.now(),
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

    seed_users(db, app)

    councils = seed_councils(db)

    posts = seed_posts(db, councils[0])

    seed_post_users(db, posts[0])

    seed_events(db, councils[1])

    seed_permissions(db, posts[0])
