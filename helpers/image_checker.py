from PIL import Image, UnidentifiedImageError  # type: ignore
from fastapi import HTTPException, UploadFile


async def validate_image(image: UploadFile):
    try:
        img = Image.open(image.file)  # type: ignore
        img.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")
    finally:
        image.file.seek(0)
