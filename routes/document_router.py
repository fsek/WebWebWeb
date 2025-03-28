from pydoc import doc
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from api_schemas import document_router
from database import DB_dependency
from db_models.document_model import Document_DB
from api_schemas.document_schema import DocumentRead, DocumentCreate, DocumentUpdate
from db_models.user_model import User_DB
from routes import ad_router
from user.permission import Permission

document_router = APIRouter()

@document_router.get("/", response_model=list[DocumentRead])
def get_all_documents(db: DB_dependency):
    documents = db.query(Document_DB).all()
    return documents

"""
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
"""

@document_router.get("/{id}", response_model=DocumentRead)
def get_document_by_id(id: int, db: DB_dependency):
    document = db.query(Document_DB).filter_by(document_id_id=id).one_or_none()
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return document

"""
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
"""

@document_router.get("/title/{stitle}", response_model=list[DocumentRead])
def get_document_by_title(stitle: str, db: DB_dependency):
    documents = db.query(Document_DB).filter(func.lower(Document_DB.title) == func.lower(stitle)).all()
    if len(documents) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return documents

"""
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


@ad_router.patch("/updateAd/{ad_id}", response_model=AdRead, dependencies=[Permission.require("manage", "Ads")])
def update_ad(ad_id: int, data: AdUpdate, db: DB_dependency):

    ad = db.query(BookAd_DB).filter_by(ad_id=ad_id).one_or_none()
    if ad is None:
        raise HTTPException(404, detail="Ad not found")

    for var, value in vars(data).items():
        setattr(ad, var, value) if value is not None else None

    db.commit()

    return ad
"""