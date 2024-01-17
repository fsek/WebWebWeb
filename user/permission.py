from typing import cast
from fastapi import Depends, HTTPException, status
from fastapi_users import jwt
from db_models.permission_model import PermissionAction, PermissionTarget
from db_models.user_model import User_DB
from user.token_strategy import JWT_SECRET, AccessTokenData, CustomTokenStrategy
from user.user_stuff import (
    current_active_verified_user,
    current_active_verified_user_token,
)


class Permission:
    @classmethod
    def base(cls):
        # Use this dependency for routes that any fsek user should access
        return Depends(current_active_verified_user)

    @classmethod
    def require(cls, action: PermissionAction, target: PermissionTarget):
        # Use this dependency on routes which require specific permissions
        def dependency(user_and_token: tuple[User_DB, str] = Depends(current_active_verified_user_token)):
            user, token = user_and_token
            permissions: list[str] = []
            for post in user.posts:
                for perm in post.permissions:
                    permissions.append(f"{perm.action}:{perm.target}")

            decoded_token = cast(AccessTokenData, jwt.decode_jwt(token, JWT_SECRET, audience=["fastapi-users:auth"]))

            # see if user has a permission matching the required permission
            for perm in decoded_token["permissions"]:
                try:
                    claim_action, claim_target = CustomTokenStrategy.decode_permission(perm)
                except:
                    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

                verified = cls.verify_permission(claim_action, claim_target, action, target)
                if verified:
                    return user

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return Depends(dependency)

    @classmethod
    def verify_permission(
        cls,
        claim_action: str,
        claim_target: str,
        required_action: PermissionAction,
        required_target: PermissionTarget,
    ) -> bool:
        # It's unlikely but possible to recieve a token with pemissions recently removed from hard-coded list
        # not a problem though since you'll notice errors on routes still accepting what you removed
        if claim_target != required_target:
            return False

        if claim_action == required_action:
            return True

        # we want manage to work for both "view" and "manage"
        if required_action == "view" and claim_action == "manage":
            return True

        return False
