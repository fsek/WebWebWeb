from fastapi import Depends, FastAPI, HTTPException
from db_models import BaseModelDB, BookInDB, UserInDB
from database import engine, get_db
from sqlalchemy.orm import Session

from schemas import AssignPayload, BookCreate, BookRead, UserCreate, UserRead

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
    user = UserInDB(name=user_in.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/assign", response_model=UserRead)
def assign_book(data: AssignPayload, db: Session = Depends(get_db)):
    book = db.query(BookInDB).filter(BookInDB.id == data.book_id).first()
    if book is None:
        raise HTTPException(404)

    user = db.query(UserInDB).filter(UserInDB.id == data.user_id).first()
    if user is None:
        raise HTTPException(404)

    user.books.append(book)

    db.commit()
    db.refresh(user)
    db.refresh(book)
    return user
