from fastapi import APIRouter
from schemas.user_schemas import UserCreate, UserRead
from user.user_stuff import USERS, auth_backend

auth_router = APIRouter()

# provides login and logout
auth_router.include_router(USERS.get_auth_router(auth_backend))  # type: ignore

# provides /register
auth_router.include_router(USERS.get_register_router(UserRead, UserCreate))

# provides /forgot-password and /reset-password
auth_router.include_router(USERS.get_reset_password_router())

# provides /request-verify-token /verify
auth_router.include_router(USERS.get_verify_router(UserRead))
