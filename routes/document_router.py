from fastapi import APIRouter, HTTPException, status
from api_schemas.document_schema import DocumentOverview, DocumentUpload
from api_schemas.user_schemas import UserAccessCreate, UserAccessRead, UserAccessUpdate
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
    "/", dependencies=[Permission.require("manage", "UserDoorAccess")], response_model=UserAccessRead
)
def update_document(db: DB_dependency, data: UserAccessUpdate):
    access = db.query(UserDoorAccess_DB).filter_by(user_access_id=data.access_id).one_or_none()

    if access is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    for var, value in vars(data).items():
        setattr(access, var, value) if value else None

    if access.stoptime < access.starttime:
        db.rollback()
        raise HTTPException(400, detail="Stop time must be later than start time")

    db.commit()
    return access


@document_archive_router.delete(
    "/", dependencies=[Permission.require("manage", "UserDoorAccess")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_access(db: DB_dependency, access_id: int):
    access = db.query(UserDoorAccess_DB).filter_by(user_access_id=access_id).one_or_none()

    if access == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(access)
    db.commit()

    return
