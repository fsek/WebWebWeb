from typing import cast
from fastapi import Depends, HTTPException, status
from fastapi_users_pelicanq import jwt
from db_models.permission_model import PERMISSION_TYPE, PERMISSION_TARGET
from db_models.user_model import User_DB
from user.token_strategy import AccessTokenData, CustomTokenStrategy, get_jwt_secret
from user.user_stuff import (
    current_user,
    current_verified_user,
    current_verified_user_token,
)


class Permission:
    @classmethod
    def primitive(cls):
        # Use this for almost only verification of email and getMe
        def dependency(user: User_DB | None = Depends(current_user)):
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            return user

        return Depends(dependency)

    @classmethod
    def base(cls):
        # Use this dependency for routes that any user, member or not, should access
        def dependency(user: User_DB | None = Depends(current_verified_user)):
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            return user

        return Depends(dependency)

    @classmethod
    def member(cls):
        # Use this dependency for routes that only members should access
        # Do not use if you want to also allow users without accounts, see check_member
        def dependency(user: User_DB | None = Depends(current_verified_user)):
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            if not user.is_member:
                raise HTTPException(status.HTTP_403_FORBIDDEN)

            return user

        return Depends(dependency)

    @classmethod
    def check_member(cls):
        # Use this dependency for routes that OPTIONALLY require member status
        # E.g. if a route should return different data for members and users without accounts
        def dependency(user: User_DB | None = Depends(current_verified_user)):
            if user is None:
                return False

            if not user.is_member:
                return False

            return user

        return Depends(dependency)

    @classmethod
    def require(cls, action: PERMISSION_TYPE, target: PERMISSION_TARGET):
        # Use this dependency on routes which require specific permissions
        def dependency(user_and_token: tuple[User_DB | None, str | None] = Depends(current_verified_user_token)):
            user, token = user_and_token
            if user is None or token is None:
                # We can raise here unlike in "check" because this is supposed to be an absolute requirement
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            permissions: list[str] = []
            for post in user.posts:
                for perm in post.permissions:
                    permissions.append(f"{perm.action}:{perm.target}")

            decoded_token = cast(
                AccessTokenData, jwt.decode_jwt(token, Depends(get_jwt_secret), audience=["fastapi-users:auth"])
            )

            # see if user has a permission matching the required permission
            for perm in decoded_token["permissions"]:
                try:
                    claim_action, claim_target = CustomTokenStrategy.decode_permission(perm)
                except:
                    raise HTTPException(status.HTTP_403_FORBIDDEN)

                verified = cls.verify_permission(claim_action, claim_target, action, target)
                if verified:
                    return user

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return Depends(dependency)

    @classmethod
    def verify_permission(
        cls,
        claim_action: str,
        claim_target: str,
        required_action: PERMISSION_TYPE,
        required_target: PERMISSION_TARGET,
    ) -> bool:
        # It's unlikely but possible to recieve a token with pemissions recently removed from hard-coded list
        # not a problem though since you'll notice errors on routes still accepting what you removed

        if claim_target != required_target and claim_target != "all":
            return False

        if claim_action == required_action or claim_action == "manage":
            return True

        return False

    @classmethod
    def check(cls, action: PERMISSION_TYPE, target: PERMISSION_TARGET):
        # Use this dependency on routes which work differently if the user has specific permissions
        def dependency(user_and_token: tuple[User_DB | None, str | None] = Depends(current_verified_user_token)):
            user, token = user_and_token
            if user is None or token is None:
                # If we raise an exception here, it would cause the whole calling function to get an exception
                # which defeats the point of this check being optional
                return False

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
                    return False

                verified = cls.verify_permission(claim_action, claim_target, action, target)
                if verified:
                    return True

            return False

        return Depends(dependency)
