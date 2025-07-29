import os
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
import datetime

from fastapi.responses import FileResponse
from sqlalchemy import and_
from api_schemas.news_schemas import NewsCreate, NewsRead, NewsUpdate
from database import DB_dependency
from db_models.news_model import News_DB
from db_models.user_model import User_DB
from helpers.constants import NEWS_PER_PAGE
from helpers.image_checker import validate_image
from helpers.rate_limit import rate_limit
from helpers.types import ALLOWED_EXT, ASSETS_BASE_PATH
from services.news_service import create_new_news, update_existing_news, bump_existing_news
from user.permission import Permission


news_router = APIRouter()


@news_router.get("/all", response_model=list[NewsRead])
def get_all_news(db: DB_dependency):
    news = db.query(News_DB).order_by(News_DB.bumped_at.desc()).all()
    return news


@news_router.get("/{news_id}", response_model=NewsRead)
def get_news(news_id: int, db: DB_dependency):
    news = db.query(News_DB).filter_by(id=news_id).one_or_none()
    if news is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return news


@news_router.post("/", response_model=NewsRead)
def create_news(data: NewsCreate, author: Annotated[User_DB, Permission.require("manage", "News")], db: DB_dependency):
    news = create_new_news(data, author.id, db)
    return news


@news_router.post("/{news_id}/image", dependencies=[Permission.require("manage", "News"), Depends(rate_limit())])
async def post_news_image(news_id: int, db: DB_dependency, image: UploadFile = File()):
    news = db.query(News_DB).get(news_id)
    if not news:
        raise HTTPException(404, "No event found")

    if image:

        await validate_image(image)

        filename: str = str(image.filename)
        _, ext = os.path.splitext(filename)

        ext = ext.lower()

        if ext not in ALLOWED_EXT:
            raise HTTPException(400, "file extension not allowed")

        dest_path = Path(f"{ASSETS_BASE_PATH}/news/{news.id}{ext}")

        dest_path.write_bytes(image.file.read())


@news_router.get("/{news_id}/image", dependencies=[Depends(rate_limit(limit=100))])
def get_news_image(news_id: int, db: DB_dependency):
    news = db.query(News_DB).get(news_id)
    if not news:
        raise HTTPException(404, "No image for this news")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "news"

    matches = list(asset_dir.glob(f"{news.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/{ASSETS_BASE_PATH}/news/{filename}"

    return Response(status_code=200, headers={"X-Accel-Redirect": internal})


@news_router.get("/{news_id}/image/stream", dependencies=[Depends(rate_limit(limit=100))])
def get_news_image_stream(news_id: int, db: DB_dependency):
    news = db.query(News_DB).get(news_id)
    if not news:
        raise HTTPException(404, "No image for this news")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "news"

    matches = list(asset_dir.glob(f"{news.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/{ASSETS_BASE_PATH}/news/{filename}"

    return FileResponse(internal)


@news_router.delete(
    "/{news_id}",
    dependencies=[Permission.require("manage", "News")],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_news(news_id: int, db: DB_dependency):
    news = db.query(News_DB).filter_by(id=news_id).one_or_none()
    if news is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(news)
    db.commit()
    return


@news_router.patch("/{news_id}", dependencies=[Permission.require("manage", "News")], response_model=NewsRead)
def update_news(news_id: int, updated_news: NewsUpdate, db: DB_dependency):
    news = update_existing_news(news_id, updated_news, db)
    return news


@news_router.patch("/bump/{news_id}", dependencies=[Permission.require("manage", "News")], response_model=NewsRead)
def bump_news(news_id: int, db: DB_dependency):
    news = bump_existing_news(news_id, db)
    return news


@news_router.get("/page/{page_nbr}", response_model=list[NewsRead])
def get_paginated_news(page_nbr: int, db: DB_dependency):

    if page_nbr < 0:
        raise HTTPException(400, detail="Invalid page number")

    offset = page_nbr * NEWS_PER_PAGE

    paginated_news = db.query(News_DB).order_by(News_DB.bumped_at.desc()).offset(offset).limit(NEWS_PER_PAGE).all()

    return paginated_news


@news_router.get("/pinned/", response_model=list[NewsRead])
def get_pinned_news(db: DB_dependency):
    now = datetime.datetime.now(datetime.UTC)
    pinned_news = (
        db.query(News_DB)
        .filter(and_(News_DB.pinned_from < now, News_DB.pinned_to > now))
        .order_by(News_DB.bumped_at.desc())
        .all()
    )
    return pinned_news
