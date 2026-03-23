# Used both in document_router and in course_document_router.

from fastapi import HTTPException
from helpers.constants import MAX_DOC_TITLE, MAX_FILE_SIZE_MB
from helpers.pdf_checker import validate_pdf_header
from fastapi import File, UploadFile, HTTPException
import os
from helpers.db_util import sanitize_title
from pathlib import Path


async def validate_file(base_path: str, file: UploadFile = File()):

    await validate_pdf_header(file)

    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    filename, ext = os.path.splitext(str(file.filename))

    sanitized_filename = sanitize_title(filename)

    if len(sanitized_filename) > MAX_DOC_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    allowed_exts = {".pdf"}

    ext = ext.lower()

    if ext not in allowed_exts:
        raise HTTPException(400, "File extension not allowed")

    if file.size is None:
        raise HTTPException(400, detail="Could not determine file size")

    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            400, detail=f"File size is too large! Compress the file to smaller than {MAX_FILE_SIZE_MB}MB"
        )

    file.filename = f"{sanitized_filename}{ext}"

    file_path = Path(f"{base_path}/{sanitized_filename}{ext}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    return sanitized_filename, ext, file_path
