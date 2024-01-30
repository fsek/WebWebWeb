from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api_schemas.news_schemas import NewsCreate
from db_models.news_model import News_DB
from helpers.date_util import force_utc, round_whole_minute


def create_new_news(data: NewsCreate, author_id: int, db: Session):
    if (data.pinned_from is None and data.pinned_to is not None) or (
        data.pinned_from is not None and data.pinned_to is None
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Either both or none of pinned_from and pinned_to must be None"
        )

    if data.pinned_from is not None and data.pinned_to is not None:
        force_utc(data.pinned_from)
        force_utc(data.pinned_to)
        data.pinned_from = round_whole_minute(data.pinned_from)
        data.pinned_to = round_whole_minute(data.pinned_to)

        if data.pinned_to <= data.pinned_from:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="pinned_to must be after pinned_from")

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
