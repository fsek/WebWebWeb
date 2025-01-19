from fastapi import APIRouter

from .user_router import user_router
from .post_router import post_router
from .permission_router import permission_router
from .auth_router import auth_router
from .event_router import event_router
from .event_signup_router import event_signup_router
from .news_router import news_router
from .cafe_shift_router import cafe_shift_router
from .song_router import song_router
from .song_category_router import song_category_router
from .img_router import img_router
from .album_router import album_router
from .ad_router import ad_router
from .car_renting_router import car_router
from .candidate_router import candidate_router
from .election_router import election_router

# here comes the big momma router
main_router = APIRouter()

main_router.include_router(user_router, prefix="/users", tags=["users"])

main_router.include_router(post_router, prefix="/posts", tags=["posts"])

main_router.include_router(permission_router, prefix="/permissions", tags=["permissions"])

main_router.include_router(auth_router, prefix="/auth", tags=["auth"])

main_router.include_router(event_router, prefix="/events", tags=["events"])

main_router.include_router(event_signup_router, prefix="/event-signup", tags=["event signup"])

main_router.include_router(news_router, prefix="/news", tags=["news"])

main_router.include_router(cafe_shift_router, prefix="/cafe-shifts", tags=["cafe"])

main_router.include_router(song_router, prefix="/songs", tags=["songs"])

main_router.include_router(song_category_router, prefix="/songs-category", tags=["songs category"])

main_router.include_router(img_router, prefix="/img", tags=["img"])

main_router.include_router(album_router, prefix="/albums", tags=["albums"])

main_router.include_router(ad_router, prefix="/ad", tags=["ads"])

main_router.include_router(car_router, prefix="/car", tags=["cars"])

main_router.include_router(election_router, prefix="/election", tags=["elections"])

main_router.include_router(candidate_router, prefix="/candidate", tags=["candidates"])
