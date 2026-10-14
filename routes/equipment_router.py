from fastapi import APIRouter, HTTPException, status
from sqlalchemy import and_, or_
from api_schemas.equipment_schema import EquipmentCreate, EquipmentRead, EquipmentUpdate
from db_models.equipment_model import Equipment_DB
from user.permission import Permission
from database import DB_dependency
from typing import Annotated
from db_models.user_model import User_DB

equipment_router = APIRouter()


@equipment_router.post("/", response_model=EquipmentRead, dependencies=[Permission.require("manage", "Equipment")])
def create_equipment(data: EquipmentCreate, db: DB_dependency):
    equipment = db.query(Equipment_DB).filter(Equipment_DB.name_sv == data.name_sv).one_or_none()
    if equipment is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is already equipment with that swedish name")
    equipment = db.query(Equipment_DB).filter(Equipment_DB.name_en == data.name_en).one_or_none()
    if equipment is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is already equipment with that english name")

    if data.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Amount must be positive")

    equipment = Equipment_DB(
        name_sv=data.name_sv,
        name_en=data.name_en,
        amount=data.amount,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(equipment)
    db.commit()
    return equipment


@equipment_router.get("/", response_model=list[EquipmentRead])
def get_all_equipment(db: DB_dependency, current_user: Annotated[User_DB, Permission.member()]):
    return db.query(Equipment_DB).all()


@equipment_router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment(equipment_id: int, db: DB_dependency, current_user: Annotated[User_DB, Permission.member()]):
    equipment = db.query(Equipment_DB).filter_by(id=equipment_id).one_or_none()
    if equipment is None:
        raise HTTPException(404, detail="Equipment not found")
    return equipment


@equipment_router.patch(
    "/update_equipment/{equipment_id}",
    response_model=EquipmentRead,
    dependencies=[Permission.require("manage", "Equipment")],
)
def update_equipment(equipment_id: int, data: EquipmentUpdate, db: DB_dependency):

    equipment = db.query(Equipment_DB).filter_by(id=equipment_id).one_or_none()
    if equipment is None:
        raise HTTPException(404, detail="Equipment not found")

    conflicting_equipment = (
        db.query(Equipment_DB)
        .filter(and_(Equipment_DB.id != equipment_id, Equipment_DB.name_sv == data.name_sv))
        .one_or_none()
    )
    if conflicting_equipment is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is another equipment with that swedish name")
    conflicting_equipment = (
        db.query(Equipment_DB)
        .filter(and_(Equipment_DB.id != equipment_id, Equipment_DB.name_en == data.name_en))
        .one_or_none()
    )
    if conflicting_equipment is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is another equipment with that english name")

    if data.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Amount must be positive")

    for var, value in vars(data).items():
        setattr(equipment, var, value) if value is not None else None

    db.commit()

    return equipment


@equipment_router.delete(
    "/{equipment_id}", response_model=EquipmentRead, dependencies=[Permission.require("manage", "Equipment")]
)
def delete_equipment(equipment_id: int, db: DB_dependency):
    equipment = db.query(Equipment_DB).filter_by(id=equipment_id).one_or_none()
    if equipment is None:
        raise HTTPException(404, detail="Equipment not found")
    db.delete(equipment)
    db.commit()
    return equipment
