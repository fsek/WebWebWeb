from fastapi import Depends, FastAPI
from car_DB import Car_DB
from car_Schemas import Car_Read, Car_Create
from database import get_db
from sqlalchemy.orm import Session

app = FastAPI()


@app.post("/addcar")
def create_car(car: Car_Create, db: Session = Depends(get_db)): #lägger till en bil i databasen av typen Car_Create
    new_car = Car_DB(user_id=car.driver_id, num_seats=car.num_seats, milage=car.milage) #jag gör ett databasobjekt

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    # database has now given new_book an id

    print('Car after adding', new_car)
    return new_car

@app.get("/car", response_model=list[Car_Read]) #response_model=Car_Read, den retunerar data i Car_Read format
def get_cars(db: Session = Depends(get_db)):
    all_cars = db.query(Car_DB).all()
    return all_cars

