from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi import Response
from database import DB_dependency, get_redis
from helpers.image_checker import validate_image
from helpers.types import ALLOWED_IMG_SIZES, ALLOWED_IMG_TYPES, ASSOCIATION_TYPES
from services.associated_img_service import upload_img, remove_img, get_single_img
from user.permission import Permission
import redis.asyncio as aioredis

associated_img_router = APIRouter()


@associated_img_router.post(
    "/", dependencies=[Permission.require("manage", "AssociatedImg")], response_model=dict[str, str]
)
async def upload_image(
    db: DB_dependency, association_type: ASSOCIATION_TYPES, association_id: int, file: UploadFile = File()
):
    await validate_image(file)
    return upload_img(db, association_type, association_id, file)


@associated_img_router.delete(
    "/{id}", dependencies=[Permission.require("manage", "AssociatedImg")], response_model=dict[str, str]
)
def delete_image(db: DB_dependency, id: int):
    return remove_img(db, id)


@associated_img_router.get("/stream/{img_id}")
def get_image_stream(
    img_id: int,
    response: Response,
    db: DB_dependency,
):
    return get_single_img(db, img_id)


@associated_img_router.get("/images/{img_id}/{size}")
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
