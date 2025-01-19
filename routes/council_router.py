from fastapi import APIRouter
from api_schemas.council_schema import CouncilExempel
from database import DB_dependency

from db_models.council_model import Council_DB

council_router = APIRouter()


@council_router.get("/exempel", response_model=CouncilExempel)
def exempel_namn(db: DB_dependency):
    db.query(Council_DB)
    return CouncilExempel(exemple_value=1)
