from fastapi import APIRouter
from api_schemas.user_schemas import UserCreate, UserRead
from user.custom_auth_router import get_auth_router
from user.user_stuff import USERS, auth_backend, refresh_backend

auth_router = APIRouter()

# provides login and logout
# auth_router.include_router(USERS.get_auth_router(refresh_backend))  # type: ignore

# provides /register
auth_router.include_router(USERS.get_register_router(UserRead, UserCreate))

# provides /forgot-password and /reset-password
auth_router.include_router(USERS.get_reset_password_router())

# provides /request-verify-token /verify
auth_router.include_router(USERS.get_verify_router(UserRead))

auth_router.include_router(
    get_auth_router(
        refresh_backend, auth_backend, USERS.get_user_manager, USERS.authenticator, requires_verification=False
    )
)


# @auth_router.post("/refresh", response_model=dict)
# async def refresh_token(
#     response: Response,
#     request: Request,
# ):
#     user_manager = USERS.get_user_manager()
#     refresh_token = request.cookies.get(cookie_transport.cookie_name)
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="Missing refresh token")

#     try:
#         payload = jwt.decode(
#             refresh_token,
#             REFRESH_SECRET,
#             algorithms=["HS256"],
#             options={"verify_signature": True, "verify_exp": False, "verify_aud": False},
#         )
#         exp = payload.get("exp")
#         if not exp:
#             raise Exception("No exp in token")
#         expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
#         now = datetime.now(timezone.utc)
#         # If less than 7 days left, rotate the refresh token
#         if expires_at - now < timedelta(days=7):
#             user = await refresh_backend.get_strategy().read_token(refresh_token, user_manager)
#             new_refresh_token = await refresh_backend.get_strategy().write_token(user_manager)
#             cookie_transport.get_login_response(response, new_refresh_token)
#         else:
#             user = await refresh_backend.get_strategy().read_token(refresh_token, user_manager)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid refresh token: " + str(e))

#     access_token = await auth_backend.get_strategy().write_token(user)
#     return {"access_token": access_token, "token_type": "bearer"}
