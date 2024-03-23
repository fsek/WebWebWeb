from fastapi import APIRouter, status
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


@ad_router.get("/{ad_id}", response_model=AdRead)
def get_ad(ad_id:int, db: DB_dependency):
    ad = db.query(BookAd_DB)
