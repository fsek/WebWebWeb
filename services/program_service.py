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


def validate_specialisation_ids(specialisation_ids: list[int], db: DB_dependency) -> tuple[list[int], list[int]]:
    """Validate that all specialisation IDs in the list exist in the database."""
    if not specialisation_ids:
        return [], []
    duplicate_specialisation_ids = _find_duplicate_ids(specialisation_ids)

    # Fetch all specialisations with the given IDs.
    specialisations = (
        db.query(Specialisation_DB).filter(Specialisation_DB.specialisation_id.in_(specialisation_ids)).all()
    )
    specialisations_by_id = {specialisation.specialisation_id: specialisation for specialisation in specialisations}

    # Check if all specialisations exist in the database.
    missing_specialisation_ids = [
        specialisation_id for specialisation_id in specialisation_ids if specialisation_id not in specialisations_by_id
    ]

    return missing_specialisation_ids, duplicate_specialisation_ids  # If not empty, we should raise error


# Note: This service requires specialisation_ids to already be validated,
# so check that they are all real specialisations already in the database before calling this.
def update_program_specialisation_associations(
    program: Program_DB,
    specialisation_ids: list[int],
    db: DB_dependency,
):

    # Keep many-to-many joins in sync with explicit add/remove in join tables.
    existing_specialisation_ids = {
        relation.specialisation_id
        for relation in db.query(ProgramSpecialisation_DB).filter_by(program_id=program.program_id).all()
    }
    specialisation_ids_to_add = [
        specialisation_id
        for specialisation_id in specialisation_ids
        if specialisation_id not in existing_specialisation_ids
    ]
    for specialisation_id in specialisation_ids_to_add:
        db.add(ProgramSpecialisation_DB(program_id=program.program_id, specialisation_id=specialisation_id))

    specialisation_ids_to_remove = [
        specialisation_id
        for specialisation_id in existing_specialisation_ids
        if specialisation_id not in specialisation_ids
    ]
    if specialisation_ids_to_remove:
        (
            db.query(ProgramSpecialisation_DB)
            .filter(
                ProgramSpecialisation_DB.program_id == program.program_id,
                ProgramSpecialisation_DB.specialisation_id.in_(specialisation_ids_to_remove),
            )
            .delete(synchronize_session=False)
        )

    return program
