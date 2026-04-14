from fastapi import APIRouter, HTTPException, status

from api_schemas.course_schema import CourseCreate, CourseRead, CourseUpdate, SimpleCourseRead
from database import DB_dependency
from db_models.course_model import Course_DB
from services.course_service import update_course_relationships, validate_relationship_ids
from user.permission import Permission


course_router = APIRouter()


@course_router.get("/", response_model=list[SimpleCourseRead])
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
    if not data.program_year_ids and not data.specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="At least one program_year_id or specialisation_id must be provided to create a course",
        )

    # Check for duplicate course code, since we require course codes to be unique.
    existing_course = db.query(Course_DB).filter_by(course_code=data.course_code).one_or_none()
    if existing_course is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Course with course_code {data.course_code} already exists, cannot create course",
        )

    # We have to validate before creating the course,
    # otherwise we might end up with orphaned courses without valid program year or specialisation associations.
    (
        missing_program_year_ids,
        missing_specialisation_ids,
        duplicate_program_year_ids,
        duplicate_specialisation_ids,
    ) = validate_relationship_ids(data, db)
    if duplicate_program_year_ids or duplicate_specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate program_year_ids: {duplicate_program_year_ids}, duplicate specialisation_ids: {duplicate_specialisation_ids}",
        )
    if missing_program_year_ids or missing_specialisation_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Program years with ids {missing_program_year_ids} and specialisations with ids {missing_specialisation_ids} not found, cannot create course",
        )

    course = Course_DB(
        title=data.title,
        course_code=data.course_code,
        description=data.description,
    )
    db.add(course)
    # Flush assigns course_id without committing
    db.flush()

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

    # Check for duplicate course code, since we require course codes to be unique.
    if data.course_code and data.course_code != course.course_code:
        existing_course = db.query(Course_DB).filter_by(course_code=data.course_code).one_or_none()
        if existing_course is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Course with course_code {data.course_code} already exists, cannot update course",
            )

    if not data.program_year_ids and not data.specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="At least one program_year_id or specialisation_id must be provided to update a course",
        )

    # We have to validate before updating the course
    (
        missing_program_year_ids,
        missing_specialisation_ids,
        duplicate_program_year_ids,
        duplicate_specialisation_ids,
    ) = validate_relationship_ids(data, db)
    if duplicate_program_year_ids or duplicate_specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate program_year_ids: {duplicate_program_year_ids}, duplicate specialisation_ids: {duplicate_specialisation_ids}",
        )
    if missing_program_year_ids or missing_specialisation_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Program years with ids {missing_program_year_ids} and specialisations with ids {missing_specialisation_ids} not found, cannot update course",
        )

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
