from typing import Generic

from fastapi import Response

from fastapi_users_pelicanq import models
from fastapi_users_pelicanq.authentication.strategy import (
    StrategyDestroyNotSupportedError,
)
from fastapi_users_pelicanq.authentication.backend import AuthenticationBackend

from user.token_strategy import RefreshStrategy


class RefreshAuthenticationBackend(AuthenticationBackend[models.UP, models.ID], Generic[models.UP, models.ID]):
    async def refresh(self, strategy: RefreshStrategy[models.UP, models.ID], user: models.UP, token: str) -> Response:
        """
        Refresh the authentication token for the user.
        This method is called when the user requests a new token using their refresh token.
        """
        try:
            new_token = await strategy.write_token(user)
            await strategy.destroy_token(token, user)
            return await self.transport.get_login_response(new_token)
        except StrategyDestroyNotSupportedError:
            raise NotImplementedError("Token refresh not supported by this strategy.")

    async def logout_all_sessions(self, strategy: RefreshStrategy[models.UP, models.ID], user: models.UP) -> Response:
        """
        Logout the user from all sessions.
        This method is called when the user requests to logout from all sessions.
        """
        try:
            await strategy.destroy_all_tokens(user)
            return await self.transport.get_logout_response()
        except StrategyDestroyNotSupportedError:
            raise NotImplementedError("Logout from all sessions not supported by this strategy.")
