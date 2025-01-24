from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api_schemas.news_schemas import NewsCreate, NewsUpdate
from db_models.news_model import News_DB
from helpers.date_util import round_whole_minute


def validate_pinned_times(pinned_from: datetime | None, pinned_to: datetime | None):
    if (pinned_from is None and pinned_to is not None) or (pinned_from is not None and pinned_to is None):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Either both or none of pinned_from and pinned_to must be None"
        )

    if pinned_from is not None and pinned_to is not None:
        pinned_from = round_whole_minute(pinned_from)
        pinned_to = round_whole_minute(pinned_to)

        if pinned_to <= pinned_from:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="pinned_to must be after pinned_from")
    return pinned_from, pinned_to


def create_new_news(data: NewsCreate, author_id: int, db: Session):
    data.pinned_from, data.pinned_to = validate_pinned_times(data.pinned_from, data.pinned_to)

    news = News_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        content_sv=data.content_sv,
        content_en=data.content_en,
        author_id=author_id,
        pinned_from=data.pinned_from,
        pinned_to=data.pinned_to,
    )
    db.add(news)
    db.commit()

    return news


def update_existing_news(news_id: int, data: NewsUpdate, db: Session):
    data.pinned_from, data.pinned_to = validate_pinned_times(data.pinned_from, data.pinned_to)

    news = db.query(News_DB).filter_by(id=news_id).one_or_none()
    if news is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # This does not allow one to "unset" values that could be null but aren't currently
    for var, value in vars(data).items():
        setattr(news, var, value) if value else None

    db.commit()
    db.refresh(news)
    return news


def bump_existing_news(news_id: int, db: Session):
    news = db.query(News_DB).filter_by(id=news_id).one_or_none()
    if news is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    setattr(news, "bumped_at", datetime.now())

    db.commit()
    db.refresh(news)
    return news
