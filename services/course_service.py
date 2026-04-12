from sqlalchemy.exc import DataError

from api_schemas.course_schema import CourseCreate, CourseUpdate
from db_models.course_model import Course_DB
from database import DB_dependency
from db_models.program_year_model import ProgramYear_DB
from db_models.specialisation_model import Specialisation_DB
from fastapi import HTTPException, status


def update_course_relationships(course: Course_DB, update_course: CourseUpdate | CourseCreate, db: DB_dependency):
    # post_ids = update_posts.post_ids
    program_year_ids = update_course.program_year_ids
    specialisation_ids = update_course.specialisation_ids

    # Fetch all program years with the given IDs
    program_years = db.query(ProgramYear_DB).filter(ProgramYear_DB.program_year_id.in_(program_year_ids)).all()
    program_years_by_id = {program_year.program_year_id: program_year for program_year in program_years}

    # Fetch all specialisations with the given IDs
    specialisations = (
        db.query(Specialisation_DB).filter(Specialisation_DB.specialisation_id.in_(specialisation_ids)).all()
    )
    specialisations_by_id = {specialisation.specialisation_id: specialisation for specialisation in specialisations}

    # Check if all program years exist in the database
    missing_program_year_ids = [
        program_year_id for program_year_id in program_year_ids if program_year_id not in program_years_by_id
    ]
    if missing_program_year_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"Program years with ids {missing_program_year_ids} not found"
        )

    # Check if all specialisations exist in the database
    missing_specialisation_ids = [
        specialisation_id for specialisation_id in specialisation_ids if specialisation_id not in specialisations_by_id
    ]
    if missing_specialisation_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"Specialisations with ids {missing_specialisation_ids} not found"
        )

    # Add new program years to the course
    for program_year_id in program_year_ids:
        program_year = program_years_by_id[program_year_id]
        if program_year not in course.program_years:
            course.program_years.append(program_year)

    # Add new specialisations to the course
    for specialisation_id in specialisation_ids:
        specialisation = specialisations_by_id[specialisation_id]
        if specialisation not in course.specialisations:
            course.specialisations.append(specialisation)

    # Remove program years not in the new list
    program_years_to_remove = [
        program_year for program_year in course.program_years if program_year.program_year_id not in program_year_ids
    ]
    for program_year in program_years_to_remove:
        course.program_years.remove(program_year)

    # Remove specialisations not in the new list
    specialisations_to_remove = [
        specialisation
        for specialisation in course.specialisations
        if specialisation.specialisation_id not in specialisation_ids
    ]
    for specialisation in specialisations_to_remove:
        course.specialisations.remove(specialisation)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Error updating course relationships (program years or specialisations)"
        )

    return course
