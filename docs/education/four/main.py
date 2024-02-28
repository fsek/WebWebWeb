from fastapi import Depends, FastAPI
from docs.education.four.database import Car_DB
from schemas import CarRead, CarCreate
from database import get_db
from sqlalchemy.orm import Session

app = FastAPI()


@app.post("/car")
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    new_car = Car_DB(driver_name=car.user, milage=0, num_seats=car.num_seats)

    # new_car has no id here

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    # database has now given new_book an id

    print("Car after adding", new_car)
    return new_car


@app.get("/car", response_model=CarRead)
def get_cars(db: Session = Depends(get_db)):
    all_cars = db.query(Car_DB).all()
    return all_cars
