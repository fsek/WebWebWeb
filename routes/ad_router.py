from fastapi import APIRouter, HTTPException, status
from api_schemas.ad_schema import AdRead
from database import DB_dependency
from db_models.ad_model import BookAd_DB
from api_schemas.event_schemas import EventCreate, EventRead, EventUpdate
from services.event_service import create_new_event, delete_event, update_event
from user.permission import Permission
from api_schemas.ad_schema import AdRead, AdCreate

event_router = APIRouter()

ad_router = APIRouter()


@ad_router.get("/", response_model=list[AdRead])
def get_all_ads(db: DB_dependency):
    adds = db.query(BookAd_DB).all()
    return adds


@ad_router.post("/", response_model=AdRead)
def create_ad(data: AdCreate, db: DB_dependency):
    ad = BookAd_DB(title = data.title, course = data.course, author = data.author, seller = data.seller, selling = data.selling, condition = data.condition, price = data.price)
    db.add(ad)
    db.commit()
    return ad


@ad_router.get("/{id}", response_model=AdRead)
def get_ad_by_id(id:int, db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ad

@ad_router.get("/{username}", response_model=list[AdRead])
def get_ad_by_user(username:str, db: DB_dependency):
    ads = db.query(BookAd_DB).filter_by(seller = username).all()
    if len(ads) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ads

@ad_router.get("/{authorname}", response_model = list[AdRead])
def get_book_ad_by_author(authorname:str, db: DB_dependency):
    ads = db.query(BookAd_DB).filter_by(author = authorname).all()
    if len(ads) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ads

@ad_router.get("/{stitle}", response_model = list[AdRead])
def get_book_ad_by_title(stitle:str, db: DB_dependency):
    ads = db.query(BookAd_DB).filter_by(title = stitle).all()
    if len(ads) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return ads


@ad_router.delete("/{id}", response_model=AdRead)
def remove_ad(id:int, db: DB_dependency):
    ad = db.query(BookAd_DB).filter_by(ad_id=id).one_or_none()
    if ad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(ad)
    db.commit()
    return ad
