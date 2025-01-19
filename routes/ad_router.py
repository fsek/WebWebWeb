from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from database import DB_dependency
from db_models.ad_model import BookAd_DB
from api_schemas.ad_schema import AdRead, AdCreate, AdUpdate
from db_models.user_model import User_DB
from user.permission import Permission

ad_router = APIRouter()


@ad_router.get("/", response_model=list[AdRead])
def get_all_ads(db: DB_dependency):
    adds = db.query(BookAd_DB).all()
    return adds


@ad_router.post("/", response_model=AdRead)
def create_ad(data: AdCreate, db: DB_dependency):
    ad = BookAd_DB(
        title=data.title,
        course=data.course,
        author=data.author,
        user_id=data.user_id,
        selling=data.selling,
        condition=data.condition,
        price=data.price,
    )
    db.add(ad)
    db.commit()
    return ad


@ad_router.get("/{id}", response_model=AdRead)
def get_ad_by_id(id: int, db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ad


@ad_router.get("/username/{username}", response_model=list[AdRead])
def get_ad_by_user(username: str, db: DB_dependency):
    user = (
        db.query(User_DB).filter(func.lower(User_DB.first_name) == func.lower(username)).one_or_none()
    )  ##func is from sqlalchemy and is used to make it to lower characters. Doesn't work with other functions
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    ads = db.query(BookAd_DB).filter_by(user_id=user.id).all()
    return ads


@ad_router.get("/authorname/{authorname}", response_model=list[AdRead])
def get_book_ad_by_author(authorname: str, db: DB_dependency):
    ads = db.query(BookAd_DB).filter(func.lower(BookAd_DB.author) == func.lower(authorname)).all()
    if len(ads) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ads


@ad_router.get("/title/{stitle}", response_model=list[AdRead])
def get_book_ad_by_title(stitle: str, db: DB_dependency):
    ads = db.query(BookAd_DB).filter(func.lower(BookAd_DB.title) == func.lower(stitle)).all()
    if len(ads) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ads


@ad_router.delete("/{id}", response_model=AdRead)
def remove_ad(id: int, current_user: Annotated[User_DB, Permission.base()], db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if ad.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    db.delete(ad)
    db.commit()

    return ad


@ad_router.delete("/manage-route/{id}", dependencies=[Permission.require("manage", "Ads")], response_model=AdRead)
def remove_ad_super_user(id: int, db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(ad)
    db.commit()
    return ad


@ad_router.put("/updateAd/{id}", response_model=AdRead)
def update_ad(id: int, data: AdUpdate, current_user: Annotated[User_DB, Permission.base()], db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if data.title is not None:
        ad.title = data.title
    if data.author is not None:
        ad.author = data.author
    if data.price is not None:
        ad.price = data.price
    if data.course is not None:
        ad.course = data.course
    if data.selling is not None:
        ad.selling = data.selling
    if data.condition is not None:
        ad.condition = data.condition
    db.commit()
    return ad
