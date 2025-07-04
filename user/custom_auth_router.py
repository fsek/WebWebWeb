from datetime import datetime, timedelta, timezone
from typing import Tuple, Type

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_users_pelicanq import models, schemas, exceptions
from fastapi_users_pelicanq.authentication import AuthenticationBackend, Authenticator, Strategy
from fastapi_users_pelicanq.manager import BaseUserManager, UserManagerDependency
from fastapi_users_pelicanq.openapi import OpenAPIResponseType
from fastapi_users_pelicanq.router.common import ErrorCode, ErrorModel
from pydantic import EmailStr
from user.refresh_auth_backend import RefreshAuthenticationBackend
from user.token_strategy import RefreshStrategy


def get_auth_router(
    backend: RefreshAuthenticationBackend[models.UP, models.ID],
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
        if cookie is not None:
            response.headers.append("set-cookie", cookie)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user."}},
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.delete("/logout", name=f"auth:{backend.name}.logout", responses=logout_responses)
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
        strategy: RefreshStrategy[models.UP, models.ID] = Depends(backend.get_strategy),
        access_strategy: Strategy[models.UP, models.ID] = Depends(access_backend.get_strategy),
    ):
        cookie = None
        user, token = refresh_token
        if await strategy.needs_refresh(token, user_manager):
            cookie = (await backend.refresh(strategy, user, token)).headers.get("set-cookie")
        response = await access_backend.login(access_strategy, user)
        # Cookie needs to be refreshed
        if cookie is not None:
            # Append the refresh token cookie to the access token response headers
            response.headers.append("set-cookie", cookie)
        await user_manager.on_after_login(user, request, response)
        return response

    @router.delete(
        "/logout-all",
        name=f"auth:{backend.name}.logout all",
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid refresh token."},
            **access_backend.transport.get_openapi_logout_responses_success(),
        },
    )
    async def logout_all(
        user_token: Tuple[models.UP, str] = Depends(get_current_refresh_user_token),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: RefreshStrategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        response = await backend.logout_all_sessions(strategy, user)
        return response

    return router


def get_update_account_router(
    backend: RefreshAuthenticationBackend[models.UP, models.ID],
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: Type[schemas.U],
    user_update_schema: Type[schemas.UU],
    authenticator: Authenticator[models.UP, models.ID],
) -> APIRouter:
    """Generate a router with update email/password routes for an authentication backend."""
    router = APIRouter()

    get_current_refresh_user_token = authenticator.current_user_token(
        active=True, verified=False, get_enabled_backends=lambda: [backend]
    )

    @router.patch(
        "/update-email",
        name=f"auth:{backend.name}.update_email",
        response_model=user_schema,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {"detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS},
                            }
                        }
                    }
                },
            }
        },
    )
    async def update_email(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        refresh_token: Tuple[models.UP, str] = Depends(get_current_refresh_user_token),
        new_email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        token_user, _ = refresh_token

        if user is None or not user.is_active or not user.id == token_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        user_update = user_update_schema(email=new_email, is_verified=False)
        try:
            updated_user = await user_manager.update(user_update, user, safe=False, request=request)
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
            )
        await user_manager.on_after_update(updated_user, user_update.create_update_dict_superuser(), request)
        return updated_user

    @router.patch(
        "/update-password",
        name=f"auth:{backend.name}.update_password",
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                                "summary": "Invalid password.",
                                "value": {"detail": ErrorCode.UPDATE_USER_INVALID_PASSWORD},
                            }
                        }
                    }
                },
            },
            **backend.transport.get_openapi_logout_responses_success(),
        },
    )
    async def update_password(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        refresh_token: Tuple[models.UP, str] = Depends(get_current_refresh_user_token),
        new_password: str = Body(..., embed=True),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: RefreshStrategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        token_user, _ = refresh_token

        if user is None or not user.is_active or not user.id == token_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        user_update = user_update_schema(password=new_password)

        try:
            updated_user = await user_manager.update(user_update, user, safe=True, request=request)
        except exceptions.InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.UPDATE_USER_INVALID_PASSWORD,
            )
        await user_manager.on_after_update(updated_user, user_update.create_update_dict(), request)
        # Probably good to logout all sessions?
        response = await backend.logout_all_sessions(strategy, updated_user)
        return response

    return router
