from fastapi import APIRouter, HTTPException, status
from api_schemas.document_schema import DocumentOverview, DocumentUpload, DocumentUpdate, DocumentLoad
from database import DB_dependency
from db_models.documents_model import Documents_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError


document_archive_router = APIRouter()


@document_archive_router.post(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], response_model=DocumentOverview
)
def upload_document(db: DB_dependency, data: DocumentUpload):

    return None


# TODO only users should be able to use this
@document_archive_router.get("/", response_model=list[DocumentOverview])
def get_all_documents(db: DB_dependency):
    accesses = db.query(Documents_DB).all()

    return accesses


@document_archive_router.patch(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], response_model=DocumentOverview
)
def update_document(db: DB_dependency, data: DocumentUpdate):
    pass


@document_archive_router.delete(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_access(db: DB_dependency, access_id: int):
    return
