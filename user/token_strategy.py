from typing import TypedDict
from fastapi_users_pelicanq.authentication import JWTStrategy
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


def get_jwt_strategy() -> JWTStrategy[User_DB, int]:
    strat = CustomTokenStrategy(secret=JWT_SECRET, lifetime_seconds=3600)
    return strat
