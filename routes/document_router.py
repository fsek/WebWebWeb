from fastapi import APIRouter, HTTPException, status
from api_schemas.document_schema import DocumentOverview, DocumentUpload, DocumentUpdate, DocumentLoad
from database import DB_dependency
from typing import Annotated
from db_models.documents_model import Documents_DB
from user.permission import Permission
from db_models.user_model import User_DB
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError
from fastapi import APIRouter, UploadFile, File
from services.img_service import upload_img, remove_img, get_single_img
from services.document_service import upload_doc, remove_doc, get_single_doc

# test
document_router = APIRouter()


""" @document_router.post(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], response_model=dict[str, str]
) """


@document_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=DocumentOverview)
def upload_document(
    db: DB_dependency, name: str, current_user: Annotated[User_DB, Permission.member()], file: UploadFile = File()
):
    return upload_doc(db, name, current_user.id, file)


""" @document_router.post(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], response_model=DocumentOverview
)
def upload_document(db: DB_dependency, data: DocumentUpload):

    return None """


# TODO only users should be able to use this
@document_router.get("/", response_model=list[DocumentOverview])
def get_all_documents(db: DB_dependency):
    documents = db.query(Documents_DB).all()

    return documents


@document_router.patch(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], response_model=DocumentOverview
)
def update_document(db: DB_dependency, data: DocumentUpdate):
    pass


@document_router.delete(
    "/", dependencies=[Permission.require("manage", "DocumentArchive")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_access(db: DB_dependency, access_id: int):
    return

@document_router.get("/{id}")
def get_doc(db: DB_dependency, id: int):
    return get_single_doc(db, id)
