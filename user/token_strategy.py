import secrets
from typing import Optional, TypedDict, Generic
from fastapi_users_pelicanq import BaseUserManager
from fastapi_users_pelicanq.authentication import JWTStrategy
from db_models.user_model import User_DB
import redis.asyncio
from fastapi_users_pelicanq.authentication import RedisStrategy, Strategy
from fastapi_users_pelicanq import models

redis_db = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)

# TODO: Use environment variables or a secure vault for secrets in production
JWT_SECRET = "MEGA SECRET"


# class to describe data in access token for our chosen JWT strategy
# sub and aud are defined by fastapi-users upon login and write_token
class AccessTokenData(TypedDict):
    sub: str
    aud: list[str]
    permissions: list[str]  # this is our own field we add for permission system


class CustomTokenStrategy(JWTStrategy[User_DB, int]):
    # on login we add our own permissions data into the JWT token
    async def get_user_permissions(self, user: User_DB) -> list[str]:
        # lets add all permissions form the user's post
        all_perms: list[str] = []
        for post in user.posts:
            for perm in post.permissions:
                all_perms.append(self.encode_permission(perm.action, perm.target))
        return all_perms

    @classmethod
    def decode_permission(cls, permission: str) -> tuple[str, str]:
        decoded = permission.split(":")
        action = decoded[0]
        target = decoded[1]
        return action, target

    @classmethod
    def encode_permission(cls, action: str, target: str) -> str:
        return f"{action}:{target}"


class RefreshStrategy(Strategy[models.UP, models.ID]):
    async def needs_refresh(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[bool]: ...  # pragma: no cover
    async def destroy_all_tokens(self, user: models.UP) -> None: ...  # pragma: no cover


class CustomRedisRefreshStrategy(
    RedisStrategy[models.UP, models.ID], RefreshStrategy[models.UP, models.ID], Generic[models.UP, models.ID]
):
    def __init__(
        self,
        redis: redis.asyncio.Redis,
        lifetime_seconds: int | None = None,
        refresh_before_seconds: int | None = None,
        *,
        key_prefix: str = "fastapi_users_token:",
    ) -> None:
        super().__init__(redis, lifetime_seconds, key_prefix=key_prefix)
        self.refresh_before_seconds = refresh_before_seconds

    async def needs_refresh(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[bool]:
        if token is None:
            return None
        if not self.refresh_before_seconds:
            return False
        key = f"{self.key_prefix}{token}"
        expiry = await self.redis.ttl(key)
        return (expiry < self.refresh_before_seconds) if expiry > 0 else None

    async def destroy_all_tokens(self, user: models.UP) -> None:
        """
        Destroy all tokens for the user.
        This method is called when the user requests to logout from all sessions.
        """
        tokens = await self.redis.smembers(f"{self.key_prefix}user:{user.id}")
        if tokens:
            await self.redis.delete(*[f"{self.key_prefix}{token}" for token in tokens])
            await self.redis.delete(f"{self.key_prefix}user:{user.id}")

    async def write_token(self, user: models.UP) -> str:
        token = secrets.token_urlsafe()
        await self.redis.set(f"{self.key_prefix}{token}", str(user.id), ex=self.lifetime_seconds)
        # Store the token in a set to be able to manage multiple tokens per user
        # This allows us to easily invalidate all tokens for a user if needed
        # ChatGPT says it is standard to use a set for this purpose ¯\_(ツ)_/¯
        await self.redis.sadd(f"{self.key_prefix}user:{user.id}", token)
        return token


def get_jwt_strategy() -> JWTStrategy[User_DB, int]:
    strat = CustomTokenStrategy(secret=JWT_SECRET, lifetime_seconds=3600)
    return strat


def get_refresh_redis_strategy() -> CustomRedisRefreshStrategy[User_DB, int]:
    # The refresh tokens do not need to contain permissions
    strat = CustomRedisRefreshStrategy[User_DB, int](redis_db, lifetime_seconds=3600 * 24 * 30)
    return strat
