from pydantic import BaseModel
from typing import List, Optional

# Base model for Teacher, contains common attributes
class TeacherBase(BaseModel):
    name: str  # Name of the teacher, a string

# Model for creating a new Teacher, inherits from TeacherBase
class TeacherCreate(TeacherBase):
    pass  # No additional attributes required for creating a teacher

# Full model for Teacher, includes attributes for both reading and writing
class Teacher(TeacherBase):
    id: int  # Unique identifier for the teacher, an integer
    class Config:
        orm_mode = True  # Allows ORM objects to be parsed to this model

# Base model for Student, contains common attributes
class StudentBase(BaseModel):
    year: int  # Year of study for the student, an integer

# Model for creating a new Student, includes additional attributes
class StudentCreate(StudentBase):
    card_pin: int  # Unique PIN for the student's card, an integer

# Full model for Student, includes attributes for both reading and writing
class Student(StudentBase):
    id: int  # Unique identifier for the student, an integer
    teachers: List[Teacher] = []  # List of teachers associated with the student
    class Config:
        orm_mode = True  # Allows ORM objects to be parsed to this model

# Base model for Book, contains common attributes
class BookBase(BaseModel):
    consumed_by_dog: bool  # Flag indicating if the book was consumed by a dog, a boolean

# Model for creating a new Book, includes additional attributes
class BookCreate(BookBase):
    student_id: Optional[int] = None  # Optional attribute indicating the student who owns the book

# Full model for Book, includes attributes for both reading and writing
class Book(BookBase):
    id: int  # Unique identifier for the book, an integer
    class Config:
        orm_mode = True  # Allows ORM objects to be parsed to this model