from fastapi import APIRouter, HTTPException, status
from api_schemas.keyval_schema import KeyvalCreate, KeyvalRead, KeyvalUpdate
from database import DB_dependency
from db_models.keyval_model import Keyval_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError


keyval_router = APIRouter()


@keyval_router.get("/", response_model=list[KeyvalRead])
def get_keyvals(db: DB_dependency):
    keyvals = db.query(Keyval_DB).all()

    return keyvals


@keyval_router.get("/{key}", response_model=KeyvalRead)
def get_keyval(db: DB_dependency, key: str):
    keyval = db.query(Keyval_DB).filter(Keyval_DB.key == key).one_or_none()

    if keyval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return keyval


@keyval_router.post("/", response_model=KeyvalRead, dependencies=[Permission.require("manage", "Keyvals")])
def post_keyval(db: DB_dependency, data: KeyvalCreate):
    present_keyval = db.query(Keyval_DB).filter(Keyval_DB.key == data.key).one_or_none()
    if present_keyval is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Key already exists")

    newkeyval = Keyval_DB(key=data.key, value=data.value)

    try:
        db.add(newkeyval)
        db.commit()
    except IntegrityError:  # prevents race condition
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Key already exists")
    return newkeyval


@keyval_router.patch("/{key}", response_model=KeyvalRead, dependencies=[Permission.require("manage", "Keyvals")])
def update_keyval(db: DB_dependency, key: str, data: KeyvalUpdate):
    keyval = db.query(Keyval_DB).filter(Keyval_DB.key == key).one_or_none()

    if keyval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    keyval.value = data.value

    db.commit()
    return keyval
