from fastapi import APIRouter, HTTPException, status
from api_schemas.book_schemas import BookCreate, BookRead
from database import DB_dependency
from db_models.book_model import Book_DB
from user.permission import Permission


book_router = APIRouter()


@book_router.get("/", response_model=list[BookRead])
def get_all_books(db: DB_dependency):
    books = db.query(Book_DB).all()
    return books


@book_router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: DB_dependency):
    book = db.query(Book_DB).filter_by(id=book_id).one_or_none()
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return book


@book_router.post("/", response_model=BookRead, dependencies=[Permission.require("manage", "Book")])
def create_book(book_data: BookCreate, db: DB_dependency):
    num_existing = db.query(Book_DB).filter(Book_DB.title == book_data.title).count()
    if num_existing > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="This post already exists")
    book = Book_DB(
        title=book_data.title,
        user=book_data.user,
        transaction=book_data.transaction,
        price=book_data.price,
        category_id=book_data.category.id,
    )
    db.add(book)
    db.commit()
    return book


@book_router.delete("/{book_id}", response_model=BookRead, dependencies=[Permission.require("manage", "Book")])
def delete_book(book_id: int, db: DB_dependency):
    book = db.query(Book_DB).filter_by(id=book_id).one_or_none()
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(book)
    db.commit()
    return book


@book_router.patch("/{book_id}", response_model=BookRead, dependencies=[Permission.require("manage", "Book")])
def update_book(book_id: int, book_data: BookCreate, db: DB_dependency):
    book = db.query(Book_DB).filter_by(id=book_id).one_or_none()
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # This does not allow one to "unset" values that could be null but aren't currently
    for var, value in vars(book_data).items():
        setattr(book, var, value) if value else None

    db.commit()
    return book
