from fastapi import HTTPException, status
from api_schemas.council_schema import CouncilExempel, CouncilRead
from database import DB_dependency
from fastapi import APIRouter

from db_models.council_model import Council_DB

council_router = APIRouter()


@council_router.get("/exempel", response_model=CouncilExempel)
def exempel_namn(db: DB_dependency):
    db.query(Council_DB)
    return CouncilExempel(exemple_value=1)


@council_router.get("/{council_id}", response_model=CouncilRead)
def get_council(council_id: int, db: DB_dependency):
    council = db.query(Council_DB).filter_by(id=council_id).one_or_none()
    if council is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return council
