from api_schemas.course_schema import CourseCreate, CourseUpdate
from db_models.course_model import Course_DB
from database import DB_dependency
from db_models.program_year_model import ProgramYear_DB
from db_models.specialisation_model import Specialisation_DB
from db_models.program_year_course_model import ProgramYearCourse_DB
from db_models.specialisation_course_model import SpecialisationCourse_DB


def _find_duplicate_ids(ids: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for value in ids:
        if value in seen and value not in duplicates:
            duplicates.append(value)
            continue
        seen.add(value)
    return duplicates


def validate_relationship_ids(update_course: CourseUpdate | CourseCreate, db: DB_dependency):
    program_year_ids = update_course.program_year_ids
    specialisation_ids = update_course.specialisation_ids

    duplicate_program_year_ids = _find_duplicate_ids(program_year_ids)
    duplicate_specialisation_ids = _find_duplicate_ids(specialisation_ids)

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

    # Check if all specialisations exist in the database
    missing_specialisation_ids = [
        specialisation_id for specialisation_id in specialisation_ids if specialisation_id not in specialisations_by_id
    ]

    return (
        missing_program_year_ids,
        missing_specialisation_ids,
        duplicate_program_year_ids,
        duplicate_specialisation_ids,
    )  # All of these lists should be empty for a valid request, otherwise we have trouble


# Note: This service requires program_year_ids and specialisation_ids to already be validated,
# so check that they are all real program years and specialisations already in the database before calling this.
def update_course_relationships(course: Course_DB, update_course: CourseUpdate | CourseCreate, db: DB_dependency):
    program_year_ids = update_course.program_year_ids
    specialisation_ids = update_course.specialisation_ids

    # Keep many-to-many joins in sync with explicit add/remove in join tables.
    existing_program_year_ids = {
        relation.program_year_id
        for relation in db.query(ProgramYearCourse_DB).filter_by(course_id=course.course_id).all()
    }
    program_year_ids_to_add = [
        program_year_id for program_year_id in program_year_ids if program_year_id not in existing_program_year_ids
    ]
    for program_year_id in program_year_ids_to_add:
        db.add(ProgramYearCourse_DB(program_year_id=program_year_id, course_id=course.course_id))

    program_year_ids_to_remove = [
        program_year_id for program_year_id in existing_program_year_ids if program_year_id not in program_year_ids
    ]
    if program_year_ids_to_remove:
        (
            db.query(ProgramYearCourse_DB)
            .filter(
                ProgramYearCourse_DB.course_id == course.course_id,
                ProgramYearCourse_DB.program_year_id.in_(program_year_ids_to_remove),
            )
            .delete(synchronize_session=False)
        )

    existing_specialisation_ids = {
        relation.specialisation_id
        for relation in db.query(SpecialisationCourse_DB).filter_by(course_id=course.course_id).all()
    }
    specialisation_ids_to_add = [
        specialisation_id
        for specialisation_id in specialisation_ids
        if specialisation_id not in existing_specialisation_ids
    ]
    for specialisation_id in specialisation_ids_to_add:
        db.add(SpecialisationCourse_DB(specialisation_id=specialisation_id, course_id=course.course_id))

    specialisation_ids_to_remove = [
        specialisation_id
        for specialisation_id in existing_specialisation_ids
        if specialisation_id not in specialisation_ids
    ]
    if specialisation_ids_to_remove:
        (
            db.query(SpecialisationCourse_DB)
            .filter(
                SpecialisationCourse_DB.course_id == course.course_id,
                SpecialisationCourse_DB.specialisation_id.in_(specialisation_ids_to_remove),
            )
            .delete(synchronize_session=False)
        )

    return course
