from typing import TypedDict
from fastapi_users.authentication import (
    JWTStrategy,
)
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from db_models.user_model import User_DB

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
        # gotta load posts through .post_users here, not through .posts.
        perms: list[str] = []
        for post_user in user.post_users:
            post: Post_DB = await post_user.awaitable_attrs.post
            permissions: list[Permission_DB] = await post.awaitable_attrs.permissions
            for perm in permissions:
                perms.append(self.encode_permission(perm.action, perm.target))
        return perms

    @classmethod
    def decode_permission(cls, permission: str) -> tuple[str, str]:
        decoded = permission.split(":")
        action = decoded[0]
        target = decoded[1]
        return action, target

    @classmethod
    def encode_permission(cls, action: str, target: str) -> str:
        return f"{action}:{target}"


def get_jwt_strategy() -> JWTStrategy[User_DB, int]:
    strat = CustomTokenStrategy(secret=JWT_SECRET, lifetime_seconds=3600)
    return strat
