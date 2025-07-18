from fastapi import APIRouter, HTTPException, status
from api_schemas.car_block_schema import CarBlockCreate, CarBlockRead
from database import DB_dependency
from typing import Annotated
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_block_model import CarBlock_DB

car_block_router = APIRouter()


@car_block_router.post("/", response_model=CarBlockRead, dependencies=[Permission.check("manage", "Car")])
def block_user_from_car_booking(
    block: CarBlockCreate,
    db: DB_dependency,
    current_user: Annotated[User_DB, Permission.member()],
):
    # Check if user exists
    user = db.query(User_DB).filter(User_DB.id == block.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    # Check if already blocked
    existing = db.query(CarBlock_DB).filter(CarBlock_DB.user_id == block.user_id).first()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="User is already blocked from car booking.")
    car_block = CarBlock_DB(user_id=block.user_id, reason=block.reason, blocked_by=current_user.id)
    db.add(car_block)
    db.commit()
    return car_block


@car_block_router.delete("/{user_id}", response_model=CarBlockRead, dependencies=[Permission.check("manage", "Car")])
def unblock_user_from_car_booking(user_id: int, db: DB_dependency):
    # Check if user exists
    user = db.query(User_DB).filter(User_DB.id == user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")
    block = db.query(CarBlock_DB).filter(CarBlock_DB.user_id == user_id).first()
    if not block:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User is not blocked.")
    db.delete(block)
    db.commit()
    return block


@car_block_router.get("/", response_model=list[CarBlockRead], dependencies=[Permission.check("manage", "Car")])
def get_all_car_booking_blocks(db: DB_dependency):
    blocks = db.query(CarBlock_DB).all()
    return list(blocks)
