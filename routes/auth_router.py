from fastapi import APIRouter, Depends
from api_schemas.user_schemas import UserCreate, UserRead
from helpers.rate_limit import rate_limit
from fastapi import APIRouter
from fastapi_users_pelicanq.schemas import BaseUserUpdate
from user.custom_auth_router import get_auth_router, get_update_account_router
from user.user_stuff import USERS, auth_backend, refresh_backend

auth_router = APIRouter()

# provides /register
auth_router.include_router(USERS.get_register_router(UserRead, UserCreate), dependencies=[Depends(rate_limit())])

# provides /forgot-password and /reset-password
auth_router.include_router(USERS.get_reset_password_router(), dependencies=[Depends(rate_limit())])

# provides /request-verify-token /verify
auth_router.include_router(USERS.get_verify_router(UserRead), dependencies=[Depends(rate_limit())])

# provides /login /logout and /refresh
auth_router.include_router(
    get_auth_router(
        refresh_backend, auth_backend, USERS.get_user_manager, USERS.authenticator, requires_verification=False
    )
)

auth_router.include_router(
    get_update_account_router(
        refresh_backend,
        auth_backend,
        USERS.get_user_manager,
        UserRead,
        BaseUserUpdate,
        USERS.authenticator,
    )
)
