from database import DB_dependency
from db_models.course_model import Course_DB
from db_models.specialisation_model import Specialisation_DB
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


def validate_course_ids(course_ids: list[int], db: DB_dependency) -> tuple[list[int], list[int]]:
    """Validate that all course IDs in the list exist in the database."""
    if not course_ids:
        return [], []
    duplicate_course_ids = _find_duplicate_ids(course_ids)

    # Fetch all courses with the given IDs.
    courses = db.query(Course_DB).filter(Course_DB.course_id.in_(course_ids)).all()
    courses_by_id = {course.course_id: course for course in courses}

    # Check if all courses exist in the database.
    missing_course_ids = [course_id for course_id in course_ids if course_id not in courses_by_id]

    return missing_course_ids, duplicate_course_ids


# Note: This service requires course_ids to already be validated,
# so check that they are all real courses already in the database before calling this.
def update_specialisation_course_associations(
    specialisation: Specialisation_DB,
    course_ids: list[int],
    db: DB_dependency,
):

    # Keep many-to-many joins in sync with explicit add/remove in join tables.
    existing_course_ids = {
        relation.course_id
        for relation in db.query(SpecialisationCourse_DB)
        .filter_by(specialisation_id=specialisation.specialisation_id)
        .all()
    }
    course_ids_to_add = [course_id for course_id in course_ids if course_id not in existing_course_ids]
    for course_id in course_ids_to_add:
        db.add(SpecialisationCourse_DB(specialisation_id=specialisation.specialisation_id, course_id=course_id))

    course_ids_to_remove = [course_id for course_id in existing_course_ids if course_id not in course_ids]
    if course_ids_to_remove:
        (
            db.query(SpecialisationCourse_DB)
            .filter(
                SpecialisationCourse_DB.specialisation_id == specialisation.specialisation_id,
                SpecialisationCourse_DB.course_id.in_(course_ids_to_remove),
            )
            .delete(synchronize_session=False)
        )

    return specialisation
