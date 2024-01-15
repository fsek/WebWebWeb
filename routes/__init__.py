from fastapi import APIRouter
from .users_router import users_router
from .posts_router import posts_router
from .admin_router import admin_router

router = APIRouter()

router.include_router(users_router, prefix="/users", tags=["users"])

router.include_router(posts_router, prefix="/posts", tags=["posts"])

router.include_router(admin_router, prefix="/admin", tags=["admin"])
