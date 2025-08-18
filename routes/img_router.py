from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi import Response
from database import DB_dependency, get_redis
from db_models.img_model import Img_DB
from helpers.image_checker import validate_image
from helpers.types import ALLOWED_IMG_SIZES, ALLOWED_IMG_TYPES
from services.img_service import upload_img, remove_img, get_single_img
from user.permission import Permission
import redis.asyncio as aioredis

img_router = APIRouter()


@img_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
async def upload_image(db: DB_dependency, album_id: int, file: UploadFile = File()):
    await validate_image(file)
    return upload_img(db, album_id, file)


@img_router.delete("/{id}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def delete_image(db: DB_dependency, id: int):
    return remove_img(db, id)


@img_router.get(
    "/album/{album_id}",
    dependencies=[Permission.member()],
    response_model=list[int],
)
async def get_album_images(
    album_id: int,
    db: DB_dependency,
    redis: aioredis.Redis = Depends(get_redis),
):
    images = db.query(Img_DB).filter(Img_DB.album_id == album_id).all()
    if not images:
        raise HTTPException(status_code=404, detail="Album not found or no images")

    ids: list[int] = []

    pipe = redis.pipeline()
    for img in images:
        pipe.set(f"img:{img.id}:path", img.path, ex=3600)
        ids.append(img.id)
    await pipe.execute()

    return ids


@img_router.get("/stream/{img_id}", dependencies=[Permission.member()])
def get_image_stream(
    img_id: int,
    response: Response,
    db: DB_dependency,
):
    return get_single_img(db, img_id)


@img_router.get(
    "/images/{img_id}/{size}",
    dependencies=[Permission.member()],
)
async def get_image(
    img_id: int,
    size: ALLOWED_IMG_TYPES,
    response: Response,
    redis: aioredis.Redis = Depends(get_redis),
) -> Response:
    if size not in ALLOWED_IMG_SIZES:
        raise HTTPException(status_code=400, detail="Invalid size")

    # only check Redis
    path = await redis.get(f"img:{img_id}:path")
    if not path:
        raise HTTPException(status_code=404, detail="Image not found or not cached")

    dims = ALLOWED_IMG_SIZES[size]
    internal = f"/internal/{dims}/{path.lstrip('/')}"

    return Response(
        status_code=status.HTTP_200_OK,
        headers={"X-Accel-Redirect": internal},
    )
