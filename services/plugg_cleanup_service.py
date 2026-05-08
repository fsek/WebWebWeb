from pathlib import Path

from sqlalchemy.orm import Session

from db_models.associated_img_model import AssociatedImg_DB
from db_models.course_model import Course_DB
from db_models.course_document_model import CourseDocument_DB
from db_models.program_model import Program_DB
from db_models.program_year_model import ProgramYear_DB
from db_models.specialisation_model import Specialisation_DB

PluggEntityWithAssociatedImage = Program_DB | ProgramYear_DB | Course_DB | Specialisation_DB


def collect_course_document_paths_and_delete_rows(
    db: Session,
    course: Course_DB,
    document_base_path: str,
) -> list[str]:
    """Delete a course's document rows and return corresponding file paths for post-commit cleanup."""
    file_paths: list[str] = []

    documents = db.query(CourseDocument_DB).filter_by(course_id=course.course_id).all()
    for document in documents:
        file_paths.append(str(Path(document_base_path) / document.file_name))
        db.delete(document)

    return file_paths


def collect_orphaned_associated_img_path_after_detach(
    db: Session,
    entity: PluggEntityWithAssociatedImage,
) -> list[str]:
    """Detach entity from its associated image and queue image file deletion if image becomes orphaned."""
    associated_img_id = entity.associated_img_id
    entity.associated_img = None

    # db_session in tests has autoflush disabled, so flush before reference checks.
    db.flush()

    img_path = _delete_associated_img_if_orphaned(db, associated_img_id)
    if img_path is None:
        return []
    return [img_path]


def remove_files(paths: list[str]) -> None:
    """Best-effort file cleanup after DB commits."""
    for path in paths:
        if not path:
            continue
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            # Deletion has already happened in DB; do not crash on file-system cleanup failures.
            continue


def _delete_associated_img_if_orphaned(db: Session, associated_img_id: int | None) -> str | None:
    if associated_img_id is None:
        return None

    img = db.query(AssociatedImg_DB).filter_by(associated_img_id=associated_img_id).one_or_none()
    if img is None:
        return None

    still_referenced = any(
        db.query(model).filter(model.associated_img_id == associated_img_id).first() is not None
        for model in (Program_DB, ProgramYear_DB, Course_DB, Specialisation_DB)
    )

    if still_referenced:
        return None

    db.delete(img)
    return img.path
