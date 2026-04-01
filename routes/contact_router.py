from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.contact_schema import ContactCreate, ContactRead, ContactUpdate
from db_models.contact_model import Contact_DB
from user.permission import Permission
from database import DB_dependency
from db_models.user_model import User_DB


contact_router = APIRouter()


@contact_router.post("/", response_model=ContactRead, dependencies=[Permission.require("manage", "Contacts")])
def create_contact(data: ContactCreate, db: DB_dependency):
    contact = db.query(Contact_DB).filter_by(contact_name=data.contact_name).one_or_none()
    if contact is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Contact name already exists")
    contact = Contact_DB(
        contact_name=data.contact_name,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        category=data.category,
    )
    db.add(contact)
    db.commit()
    return contact


@contact_router.get("/", response_model=list[ContactRead])
def get_all_contacts(current_user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    return db.query(Contact_DB).all()


@contact_router.get("/{contact_id}", response_model=ContactRead)
def get_contact(current_user: Annotated[User_DB, Permission.member()], contact_id: int, db: DB_dependency):
    contact = db.query(Contact_DB).filter_by(id=contact_id).one_or_none()
    if contact is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return contact


@contact_router.patch(
    "/update_contact/{contact_id}", response_model=ContactRead, dependencies=[Permission.require("manage", "Contacts")]
)
def update_contact(contact_id: int, data: ContactUpdate, db: DB_dependency):

    contact = db.query(Contact_DB).filter_by(id=contact_id).one_or_none()
    if contact is None:
        raise HTTPException(404, detail="Contact not found")

    for var, value in vars(data).items():
        setattr(contact, var, value) if value is not None else None

    db.commit()

    return contact


@contact_router.delete(
    "/{contact_id}", response_model=ContactRead, dependencies=[Permission.require("super", "Contacts")]
)
def delete_contact(contact_id: int, db: DB_dependency):
    contact = db.query(Contact_DB).filter_by(id=contact_id).one_or_none()
    db.delete(contact)
    db.commit()
    return contact
