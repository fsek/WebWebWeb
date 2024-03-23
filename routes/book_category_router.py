from database import DB_dependency
from api_schemas.book_category_schemas import BookCategoryCreate, BookCategoryRead
from db_models.book_category_model import BookCategory_DB
from fastapi import APIRouter, HTTPException, status
from user.permission import Permission


book_category_router = APIRouter()


@book_category_router.get("/", response_model=list[BookCategoryRead])
def get_all_book_categories(db: DB_dependency):
    categories = db.query(BookCategory_DB).all()
    return categories


@book_category_router.get("/{category_id}", response_model=BookCategoryRead)
def get_book_category(category_id: int, db: DB_dependency):
    category = db.query(BookCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return category


@book_category_router.post("/", response_model=BookCategoryRead, dependencies=[Permission.require("manage", "Book")])
def create_book_category(book_category_data: BookCategoryCreate, db: DB_dependency):
    num_existing = db.query(BookCategory_DB).filter(BookCategory_DB.name == book_category_data.name).count()
    if num_existing > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="This post already exists")
    bookcategory = BookCategory_DB(name=book_category_data.name)
    db.add(bookcategory)
    db.commit()
    return bookcategory


@book_category_router.delete(
    "/{category_id}", response_model=BookCategoryRead, dependencies=[Permission.require("manage", "Book")]
)
def delete_book_category(category_id: int, db: DB_dependency):
    category = db.query(BookCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # Moves books belonging to deleted category to default category
    for book in category.books:
        book.category_id = None

    db.delete(category)
    db.commit()
    return category


@book_category_router.patch(
    "/{category_id}", response_model=BookCategoryRead, dependencies=[Permission.require("manage", "Book")]
)
def update_book_category(category_id: int, category_data: BookCategoryCreate, db: DB_dependency):
    category = db.query(BookCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    category.name = category_data.name
    db.commit()
    return category
