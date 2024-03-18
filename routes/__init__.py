from fastapi import APIRouter
from .user_router import user_router
from .post_router import post_router
from .permission_router import permission_router
from .auth_router import auth_router
from .event_router import event_router
from .event_signup_router import event_signup_router
from .news_router import news_router
from .song_router import song_router
from .song_category_router import song_category_router
from .img_router import img_router
from .album_router import album_router

# here comes the big momma router
main_router = APIRouter()

main_router.include_router(user_router, prefix="/users", tags=["users"])

main_router.include_router(post_router, prefix="/posts", tags=["posts"])

main_router.include_router(permission_router, prefix="/permissions", tags=["permissions"])

main_router.include_router(auth_router, prefix="/auth", tags=["auth"])

main_router.include_router(event_router, prefix="/events", tags=["events"])

main_router.include_router(event_signup_router, prefix="/event-signup", tags=["event signup"])

main_router.include_router(news_router, prefix="/news", tags=["news"])

main_router.include_router(song_router, prefix="/songs", tags=["songs"])

main_router.include_router(song_category_router, prefix="/songs-category", tags=["songs category"])

main_router.include_router(img_router, prefix="/img", tags=["img"])

main_router.include_router(album_router, prefix="/albums", tags=["albums"])
