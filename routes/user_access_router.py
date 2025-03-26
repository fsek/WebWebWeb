from fastapi import APIRouter, HTTPException, status
from api_schemas.user_schemas import UserAccessCreate, UserAccessRead, UserAccessUpdate
from database import DB_dependency
from db_models.user_door_access_model import UserDoorAccess_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError, StatementError, SQLAlchemyError


user_access_router = APIRouter()


@user_access_router.post(
    "/", dependencies=[Permission.require("manage", "UserDoorAccess")], response_model=UserAccessRead
)
def post_user_access(db: DB_dependency, data: UserAccessCreate):

    if data.starttime >= data.stoptime:
        raise HTTPException(400, detail="Stop time must be later than start time")

    newAccess = UserDoorAccess_DB(
        user_id=data.user_id, door=data.door, starttime=data.starttime, stoptime=data.stoptime
    )

    try:
        db.add(newAccess)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Invalid data provided")
    except StatementError:
        db.rollback()
        raise HTTPException(400, detail="Invalid data type provided")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, detail="A database error occurred")

    return newAccess


@user_access_router.get(
    "/", dependencies=[Permission.require("view", "UserDoorAccess")], response_model=list[UserAccessRead]
)
def get_all_user_accesses(db: DB_dependency):
    accesses = db.query(UserDoorAccess_DB).all()

    return accesses


@user_access_router.patch(
    "/", dependencies=[Permission.require("manage", "UserDoorAccess")], response_model=UserAccessRead
)
def update_user_access(db: DB_dependency, data: UserAccessUpdate):
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


@user_access_router.delete(
    "/", dependencies=[Permission.require("manage", "UserDoorAccess")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_access(db: DB_dependency, access_id: int):
    access = db.query(UserDoorAccess_DB).filter_by(user_access_id=access_id).one_or_none()

    if access == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(access)
    db.commit()

    return
