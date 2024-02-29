from fastapi import Depends,FastAPI, HTTPException
from fastapi_users import schemas
from sqlalchemy.orm import Session
from . import exam_schemas as schemas
from . import exam_DB as models

from database import get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """
    Create a new teacher.

    Args:
        teacher (schemas.TeacherCreate): The data for creating a new teacher.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.Teacher: The created teacher.
    """
    db_teacher = models.Teacher(teacher)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student in the database.

    Args:
        student (schemas.StudentCreate): The student data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.Student: The created student.
    """
    db_student = models.Student(student)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book.

    Parameters:
    - book: The book data to be created.
    - db: The database session.

    Returns:
    - The created book.
    """
    db_book = models.Book(book)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/teachers/", response_model=schemas.Teacher)
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of teachers.

    Parameters:
    - skip (int): Number of teachers to skip (default: 0)
    - limit (int): Maximum number of teachers to retrieve (default: 100)
    - db (Session): Database session

    Returns:
    - List of teachers
    """
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers

@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific teacher by their ID.

    Args:
        teacher_id (int): The ID of the teacher to retrieve.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.Teacher: The retrieved teacher.
    """
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    return teacher

# This route updates a book's details
@app.patch("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, consumedByADog: bool, db: Session = Depends(get_db)):
    """
    Update a book in the database.

    Args:
        book_id (int): The ID of the book to update.
        body (bool): Whether the book has been consumed by a dog.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        schemas.Book: The updated book.
    """
    # Query the database for the book with the given id
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    # Iterate over the fields in the request body
    setattr(db_book, 'consumed_by_dog', consumedByADog)
    # Commit the changes to the database
    db.commit()
    # Return the updated book
    return db_book

# This route assigns a book to a student
@app.patch("/borrow-book", response_model=schemas.Book)
def borrow_book(bookToBorrowId: int, studentId: int, db: Session = Depends(get_db)):
    """
    Endpoint to borrow a book by assigning it to a student.

    Parameters:
    - bookToBorrowId (int): The ID of the book to be borrowed.
    - studentId (int): The ID of the student who is borrowing the book.
    - db (Session): The database session.

    Returns:
    - Book: The updated book object after it has been assigned to the student.
    """
    
    # Query the database for the book with the given id
    db_book = db.query(models.Book).get(bookToBorrowId)

    # Check if db_book is not None

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    else:
        # Assign the book to the student
        db_book.student_id = studentId
    
        # Commit the changes to the database
        db.commit()
    
    # Return the updated book
    return db_book


@app.patch("/pair-up", response_model=schemas.Student)
def pair_up(studentId: int, teacherId: int, db: Session = Depends(get_db)):
    """
    Pair up a student with a teacher.

    Args:
        studentId (int): The ID of the student.
        teacherId (int): The ID of the teacher.
        db (Session): The database session.

    Returns:
        schemas.Student: The updated student object.

    Raises:
        HTTPException: If the student is not found.
    """
    db_student = db.query(models.Student).filter(models.Student.id == studentId).first()
    db_teacher = db.query(models.Teacher).filter(models.Teacher.id == teacherId).first()

    # If the student does not exist, return an error
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    else:
        db_student.teachers.append(db_teacher)

    db.commit()

    return db_student