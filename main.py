from fastapi import FastAPI, Depends
from db_models import BaseModelDB, Student_DB, Teacher_DB, Book_DB
from database import engine, get_db
from sqlalchemy.orm import Session

from schemas import *


app = FastAPI()

# Create database tables
BaseModelDB.metadata.create_all(engine)
# Note: SQLite database structre cannot be updated. Delete and run again to update


@app.get("/teachers", response_model=list[TeacherOut])
def get_teachers(db: Session = Depends(get_db)):
    all_teachers = db.query(Teacher_DB).all()
    return all_teachers


@app.get("/teachers/{teacher_id}", response_model=TeacherOut)
def get_teacher_by_id(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher_DB).filter(Teacher_DB.id == teacher_id).first()
    return teacher


@app.post("/students/{student_year}/{student_card_pin}", response_model=StudentCreate)
async def make_student(
    student_year: int, student_card_pin: int, db: Session = Depends(get_db)
):
    new_student = Student_DB(year=student_year, card_pin=student_card_pin)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@app.post("/teachers/{teacher_name}", response_model=TeacherOut)
async def make_teacher(teacher_name: str, db: Session = Depends(get_db)):
    new_teacher = Teacher_DB(name=teacher_name)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@app.post("/books", response_model=BookOut)
async def make_book(db: Session = Depends(get_db)):
    new_book = Book_DB(consumed_by_dog=False)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.patch("/books/{book_id}", response_model=BookOut)
def make_book_gone(book_id: int, db: Session = Depends(get_db)):
    old_book = db.query(Book_DB).filter(Book_DB.id == book_id).first()
    if old_book:
        old_book.consumed_by_dog = True
    db.commit()
    db.refresh(old_book)
    return old_book


@app.patch("/borrow-book/{student_id}/{book_id}", response_model=BookOut)
def borrow_book(student_id: int, book_id: int, db: Session = Depends(get_db)):
    student = db.query(Student_DB).filter(Student_DB.id == student_id).first()
    if student == None:
        return {"message": "Student not found"}
    book = db.query(Book_DB).filter(Book_DB.id == book_id).first()
    if book == None:
        return {"message": "Book not found"}
    book.student_id = student.id
    db.commit()
    db.refresh(book)
    return book


@app.patch("/pair-up/{student_id}/{teacher_id}")
def pair_up(student_id: int, teacher_id: int, db: Session = Depends(get_db)):
    student = db.query(Student_DB).filter(Student_DB.id == student_id).first()
    if student == None:
        return {"message": "Student not found"}
    teacher = db.query(Teacher_DB).filter(Teacher_DB.id == teacher_id).first()
    if teacher == None:
        return {"message": "Teacher not found"}
    teacher.student.append(student)
    db.commit()
    db.refresh(teacher)
    return {"student.id": student.id, "teacher.id": teacher.id}


@app.delete("/student/{student_id}")
def make_dummy_disappear(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student_DB).filter(Student_DB.id == student_id).first()
    if student == None:
        return {"message": "Student not found"}
    if len(student.books) == 0:
        return {"message": "Student has no books"}
    for book in student.books:
        if book.consumed_by_dog:
            db.delete(student)
            db.commit()
            return {"message": "Student successfully removed"}
