from fastapi import Depends, FastAPI
from db_models import BaseModelDB, BookInDB, UserInDB
from database import engine, get_db
from sqlalchemy.orm import Session

from schemas import BookCreate, BookRead, UserCreate, UserRead

app = FastAPI()

# Create database tables
BaseModelDB.metadata.create_all(engine)
# Note: SQLite database structre cannot be updated. Delete and run again to update


@app.get("/user", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    all_users = db.query(UserInDB).all()
    return all_users


@app.get("/book", response_model=list[BookRead])
def get_books(db: Session = Depends(get_db)):
    all_books = db.query(BookInDB).all()
    return all_books


@app.post("/book", response_model=BookRead)
def create_one_book(book_in: BookCreate, db: Session = Depends(get_db)):
    book = BookInDB(title=book_in.title)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.post("/user", response_model=UserRead)
def create_one_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserInDB(name=user_in.name, age=user_in.age, password=user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
