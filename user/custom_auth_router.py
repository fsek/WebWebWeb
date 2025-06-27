from datetime import datetime, timedelta, timezone
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users_pelicanq import models
from fastapi_users_pelicanq.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users_pelicanq.manager import BaseUserManager, UserManagerDependency
from fastapi_users_pelicanq.openapi import OpenAPIResponseType
from fastapi_users_pelicanq.router.common import ErrorCode, ErrorModel
import jwt
from user.token_strategy import REFRESH_SECRET


def get_auth_router(
    backend: AuthenticationBackend[models.UP, models.ID],
    access_backend: AuthenticationBackend[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator[models.UP, models.ID],
    requires_verification: bool = False,
) -> APIRouter:
    """Generate a router with login/logout routes for an authentication backend."""
    router = APIRouter()
    get_current_refresh_user_token = authenticator.current_user_token(
        active=True, verified=requires_verification, get_enabled_backends=lambda: [backend]
    )

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **access_backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        access_strategy: Strategy[models.UP, models.ID] = Depends(access_backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await access_backend.login(access_strategy, user)
        cookie = (await backend.login(strategy, user)).headers.get("set-cookie")
        if not cookie:
            return response
        response.headers.append("set-cookie", cookie)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user."}},
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post("/logout", name=f"auth:{backend.name}.logout", responses=logout_responses)
    async def logout(
        user_token: Tuple[models.UP, str] = Depends(get_current_refresh_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    @router.post(
        "/refresh",
        name=f"auth:{backend.name}.refresh",
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid refresh token."},
            **access_backend.transport.get_openapi_login_responses_success(),
        },
    )
    async def refresh(
        request: Request,
        refresh_token: Tuple[models.UP, str] = Depends(get_current_refresh_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
        access_strategy: Strategy[models.UP, models.ID] = Depends(access_backend.get_strategy),
    ):
        user, token = refresh_token
        cookie = None
        response = await access_backend.login(access_strategy, user)
        try:
            payload = jwt.decode(
                token,
                key=REFRESH_SECRET,
                algorithms=["HS256"],
                options={"verify_signature": True, "verify_exp": True, "verify_aud": False},
            )
            exp = payload.get("exp")
            if not exp:
                raise Exception("No exp in token")
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            # If less than 7 days left, rotate the refresh token
            if expires_at - now < timedelta(days=7):
                cookie = (await backend.login(strategy, user)).headers.get("set-cookie")
        except Exception as e:
            return response
        if not cookie:
            return response
        response.headers.append("set-cookie", cookie)
        await user_manager.on_after_login(user, request, response)
        return response

    return router
