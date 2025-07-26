from fastapi import UploadFile, HTTPException


async def validate_pdf_header(file: UploadFile):
    header = await file.read(4)  # read first 4 bytes
    await file.seek(0)  # rewind for later
    if header != b"%PDF":
        raise HTTPException(400, "File is not a valid PDF")
