from fastapi import APIRouter, HTTPException, status

from api_schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from database import DB_dependency
from db_models.course_model import Course_DB
from services.course_service import update_course_relationships
from user.permission import Permission


course_router = APIRouter()


@course_router.get("/", response_model=list[CourseRead])
def get_all_courses(db: DB_dependency):
    return db.query(Course_DB).all()


@course_router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: DB_dependency):
    course = db.query(Course_DB).filter_by(course_id=course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return course


@course_router.post("/", response_model=CourseRead, dependencies=[Permission.require("manage", "Plugg")])
def create_course(data: CourseCreate, db: DB_dependency):
    course = Course_DB(
        title=data.title,
        course_code=data.course_code,
        description=data.description,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # We handle program_year_ids and specialisation_ids separately, since they are many-to-many relationships.
    course = update_course_relationships(course, data, db)

    db.commit()
    db.refresh(course)

    return course


@course_router.patch("/{course_id}", response_model=CourseRead, dependencies=[Permission.require("manage", "Plugg")])
def update_course(course_id: int, data: CourseUpdate, db: DB_dependency):
    course = db.query(Course_DB).filter_by(course_id=course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    for var, value in vars(data).items():
        if var != "program_year_ids" and var != "specialisation_ids":
            # Note that we always set None values, to clear fields if the user wants to.
            setattr(course, var, value)

    # We handle program_year_ids and specialisation_ids separately, since they are many-to-many relationships.
    course = update_course_relationships(course, data, db)

    db.commit()
    db.refresh(course)
    return course


@course_router.delete("/{course_id}", response_model=CourseRead, dependencies=[Permission.require("manage", "Plugg")])
def delete_course(course_id: int, db: DB_dependency):
    course = db.query(Course_DB).filter_by(course_id=course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(course)
    db.commit()
    return course
