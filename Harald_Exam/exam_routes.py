from fastapi import Depends,FastAPI
from fastapi_users import schemas
from sqlalchemy.orm import Session
from . import exam_schemas as schemas
from . import exam_DB as models

from database import get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = models.Teacher(teacher)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(student)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(book)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/teachers/", response_model=schemas.Teacher)
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).offset(skip).limit(limit).all()
    return teachers

@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    return teacher