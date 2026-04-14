from database import DB_dependency
from db_models.specialisation_model import Specialisation_DB
from db_models.program_model import Program_DB
from db_models.program_specialisation_model import ProgramSpecialisation_DB


def _find_duplicate_ids(ids: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for value in ids:
        if value in seen and value not in duplicates:
            duplicates.append(value)
            continue
        seen.add(value)
    return duplicates


def validate_program_ids(program_ids: list[int], db: DB_dependency):
    """Helper function to validate that all program IDs in the list exist in the database."""
    duplicate_program_ids = _find_duplicate_ids(program_ids)

    # Fetch all programs with the given IDs
    programs = db.query(Program_DB).filter(Program_DB.program_id.in_(program_ids)).all()
    programs_by_id = {program.program_id: program for program in programs}

    # Check if all programs exist in the database
    missing_program_ids = [program_id for program_id in program_ids if program_id not in programs_by_id]

    return missing_program_ids, duplicate_program_ids  # If not empty, we have trouble


# Note: This service requires program_ids to already be validated,
# so check that they are all real programs already in the database before calling this.
def update_specialisation_program_associations(
    specialisation: Specialisation_DB,
    program_ids: list[int],
    db: DB_dependency,
):

    # Keep many-to-many joins in sync with explicit add/remove in join tables.
    existing_program_ids = {
        relation.program_id
        for relation in db.query(ProgramSpecialisation_DB)
        .filter_by(specialisation_id=specialisation.specialisation_id)
        .all()
    }
    program_ids_to_add = [program_id for program_id in program_ids if program_id not in existing_program_ids]
    for program_id in program_ids_to_add:
        db.add(ProgramSpecialisation_DB(program_id=program_id, specialisation_id=specialisation.specialisation_id))

    program_ids_to_remove = [program_id for program_id in existing_program_ids if program_id not in program_ids]
    if program_ids_to_remove:
        (
            db.query(ProgramSpecialisation_DB)
            .filter(
                ProgramSpecialisation_DB.specialisation_id == specialisation.specialisation_id,
                ProgramSpecialisation_DB.program_id.in_(program_ids_to_remove),
            )
            .delete(synchronize_session=False)
        )

    return specialisation
