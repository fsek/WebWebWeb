from fastapi import APIRouter, HTTPException, status

from api_schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from database import DB_dependency
from db_models.course_model import Course_DB
from user.permission import Permission
from helpers.url_formatter import url_formatter
from db_models.program_year_model import ProgramYear_DB
from db_models.specialisation_course_model import SpecialisationCourse_DB
from db_models.specialisation_model import Specialisation_DB
from db_models.program_year_course_model import ProgramYearCourse_DB


course_router = APIRouter()


@course_router.get("/", response_model=list[CourseRead])
def get_all_courses(db: DB_dependency):
    return db.query(Course_DB).all()


@course_router.get("/by_program_year/{program_year_id}", response_model=list[CourseRead])
def get_courses_by_program_year(program_year_id: int, db: DB_dependency):
    program_year = db.query(ProgramYear_DB).filter_by(program_year_id=program_year_id).one_or_none()
    if program_year is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Program year not found")

    return (
        db.query(Course_DB)
        .join(Course_DB.program_year_courses)
        .filter(ProgramYearCourse_DB.program_year_id == program_year_id)
        .all()
    )


@course_router.get("/by_specialisation/{specialisation_id}", response_model=list[CourseRead])
def get_courses_by_specialisation(specialisation_id: int, db: DB_dependency):
    specialisation = db.query(Specialisation_DB).filter_by(specialisation_id=specialisation_id).one_or_none()
    if specialisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Specialisation not found")

    return (
        db.query(Course_DB)
        .join(Course_DB.specialisation_courses)
        .filter(SpecialisationCourse_DB.specialisation_id == specialisation_id)
        .all()
    )


@course_router.get("/by_url_title/{title}", response_model=CourseRead)
def get_course_by_url_title(title: str, db: DB_dependency):
    normalized_title = url_formatter(title)
    course = db.query(Course_DB).filter_by(title_urlized=normalized_title).one_or_none()

    if course is not None:
        return course

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@course_router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: DB_dependency):
    course = db.query(Course_DB).filter_by(course_id=course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return course


@course_router.post("/", response_model=CourseRead, dependencies=[Permission.require("manage", "Plugg")])
def create_course(data: CourseCreate, db: DB_dependency):
    normalized_title = url_formatter(data.title)

    # Check for duplicate course title using url-formatter, so title uniqueness
    # matches URL lookup conventions used elsewhere in plugg routes.
    existing_title = db.query(Course_DB).filter_by(title_urlized=normalized_title).first()
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Course title already exists")

    # Check for duplicate course code, since we require course codes to be unique.
    existing_course = db.query(Course_DB).filter_by(course_code=data.course_code).first()
    if existing_course is not None and data.course_code is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Course with course_code {data.course_code} already exists, cannot create course",
        )

    course = Course_DB(
        title=data.title,
        title_urlized=normalized_title,
        course_code=data.course_code,
        description=data.description,
    )
    db.add(course)

    db.commit()
    db.refresh(course)

    return course


@course_router.patch("/{course_id}", response_model=CourseRead, dependencies=[Permission.require("manage", "Plugg")])
def update_course(course_id: int, data: CourseUpdate, db: DB_dependency):
    course = db.query(Course_DB).filter_by(course_id=course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    normalized_title = url_formatter(data.title)

    # Check for duplicate course title using url-formatter. Ignore the current course when checking.
    existing_title = (
        db.query(Course_DB).filter(Course_DB.course_id != course_id).filter_by(title_urlized=normalized_title).first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Course title already exists")

    # Check for duplicate course code, since we require course codes to be unique.
    if data.course_code and data.course_code != course.course_code:
        existing_course = db.query(Course_DB).filter_by(course_code=data.course_code).first()
        if existing_course is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Course with course_code {data.course_code} already exists, cannot update course",
            )

    for var, value in vars(data).items():
        # Note that we always set None values, to clear fields if the user wants to.
        setattr(course, var, value)

    course.title_urlized = normalized_title

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
