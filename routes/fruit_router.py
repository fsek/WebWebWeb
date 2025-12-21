from fastapi import APIRouter, HTTPException, status
from api_schemas.fruit_schema import FruitCreate, FruitRead, FruitUpdate
from database import DB_dependency
from db_models.fruit_model import Fruit_DB
from user.permission import Permission


fruit_router = APIRouter()


@fruit_router.get("/", response_model=list[FruitRead])
def get_all_fruits(db: DB_dependency):
    fruit = db.query(Fruit_DB).all()
    return fruit


@fruit_router.get("/{fruit_id}", response_model=FruitRead)
def get_fruit(fruit_id: int, db: DB_dependency):
    fruit = db.query(Fruit_DB).filter_by(id=fruit_id).one_or_none()
    if fruit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return fruit


@fruit_router.post("/", response_model=FruitRead, dependencies=[Permission.require("manage", "Fruit")])
def create_fruit(fruit_data: FruitCreate, db: DB_dependency):
    fruit = Fruit_DB(
        name=fruit_data.name,
        color=fruit_data.color,
        price=fruit_data.price,
    )
    db.add(fruit)
    db.commit()
    return fruit


@fruit_router.delete("/{fruit_id}", response_model=FruitRead, dependencies=[Permission.require("manage", "Fruit")])
def delete_fruit(fruit_id: int, db: DB_dependency):
    fruit = db.query(Fruit_DB).filter_by(id=fruit_id).one_or_none()
    if fruit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(fruit)
    db.commit()
    return fruit


@fruit_router.patch("/{fruit_id}", response_model=FruitRead, dependencies=[Permission.require("manage", "Fruit")])
def update_fruit(fruit_id: int, fruit_data: FruitUpdate, db: DB_dependency):
    fruit = db.query(Fruit_DB).filter_by(id=fruit_id).one_or_none()
    if fruit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # This does not allow one to "unset" values that could be null but aren't currently
    for var, value in vars(fruit_data).items():
        if value is not None:
            setattr(fruit, var, value)

    db.commit()
    return fruit
