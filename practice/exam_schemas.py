from pydantic import BaseModel
from typing import List, Optional

class TeacherBase(BaseModel):
    name: str

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int
    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    year: int

class StudentCreate(StudentBase):
    card_pin: int

class Student(StudentBase):
    id: int
    teachers: List[Teacher] = []
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    consumed_by_dog: bool

class BookCreate(BookBase):
    student_id: Optional[int] = None

class Book(BookBase):
    id: int
    class Config:
        orm_mode = True