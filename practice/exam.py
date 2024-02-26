from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

## Hej ny ändring 
# Define the association table for the many-to-many relationship between Student and Teacher
student_teacher_table = Table('student_teacher', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('teacher_id', Integer, ForeignKey('teachers.id'))
)

class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    students = relationship('Student', secondary=student_teacher_table, back_populates='teachers')

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    card_pin = Column(Integer)
    teachers = relationship('Teacher', secondary=student_teacher_table, back_populates='students')
    books = relationship('Book', back_populates='student')

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    consumed_by_dog = Column(Boolean)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', back_populates='books')