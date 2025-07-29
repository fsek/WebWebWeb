from __future__ import annotations

from re import L
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from google.oauth2 import service_account

# pyright: reportMissingTypeStubs=false
# pyright: reportGeneralTypeIssues=false

from googleapiclient.discovery import build  # type: ignore
from numpy import add
from pydantic import EmailStr
from api_schemas.mail_alias_schema import AliasRead
import os

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS_PATH", "no_credentials.json")
ADMIN_EMAIL = os.getenv("GOOGLE_ADMIN_EMAIL", "admin@onlyworksinprod.com")
DOMAIN = ADMIN_EMAIL.split("@")[1]

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
    "https://www.googleapis.com/auth/apps.groups.settings",
]

mail_alias_router = APIRouter()


def get_directory_service() -> Any:
    credentials = service_account.Credentials.from_service_account_file(  # pyright: ignore[reportUnknownMemberType]
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=ADMIN_EMAIL
    )
    return build("admin", "directory_v1", credentials=credentials)  # pyright: ignore[reportUnknownVariableType]


def get_groups_settings_service() -> Any:
    credentials = service_account.Credentials.from_service_account_file(  # pyright: ignore[reportUnknownMemberType]
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=ADMIN_EMAIL
    )
    return build("groupssettings", "v1", credentials=credentials)  # pyright: ignore[reportUnknownVariableType]


@mail_alias_router.post("/alias", response_model=AliasRead)
def create_alias(
    alias: EmailStr,
    directory_service: Any = Depends(get_directory_service),
    settings_service: Any = Depends(get_groups_settings_service),
) -> Response:
    try:
        directory_service.groups().insert(
            body={"email": alias, "name": f"Mailalias: {alias}"},
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Group (alias) creation failed: {e}")

    try:
        settings_service.groups().patch(
            groupUniqueId=alias,
            body={
                "whoCanPostMessage": "ANYONE_CAN_POST",
                "allowExternalMembers": "true",
                "isArchived": "false",
            },
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Alias settings update failed: {e}")

    return Response(status_code=status.HTTP_201_CREATED)


@mail_alias_router.get("/aliases", response_model=List[AliasRead])
def list_aliases(
    service: Any = Depends(get_directory_service),
) -> List[AliasRead]:
    aliases: List[AliasRead] = []
    try:
        results = service.groups().list(domain=DOMAIN).execute()
        groups = results.get("groups", [])
        for group in groups:
            name = group.get("name", "")
            if not name.startswith("Mailalias: "):
                continue
            email = group.get("email")
            if not email:
                continue
            try:
                members_result = service.members().list(groupKey=email).execute()
                members = [m.get("email") for m in members_result.get("members", []) if m.get("email")]
                aliases.append(AliasRead(alias=email, members=members))
            except Exception:
                continue
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Listing aliases failed: {e}")
    return aliases


@mail_alias_router.delete("/alias/{alias_email}")
def delete_alias(
    alias_email: str,
    service: Any = Depends(get_directory_service),
) -> Dict[str, str]:
    g = service.groups().get(groupKey=alias_email).execute()
    if not g.get("name", "").startswith("Mailalias: "):
        raise HTTPException(status_code=403, detail=f"Cannot delete group {alias_email}: not a mail‑alias")
    try:
        service.groups().delete(groupKey=alias_email).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete alias: {e}")
    return {"status": "deleted", "alias": alias_email}


@mail_alias_router.post("/alias/{alias_email}/add_member", response_model=AliasRead)
def add_member(
    alias_email: str,
    member_email: EmailStr,
    service: Any = Depends(get_directory_service),
) -> AliasRead:
    g = service.groups().get(groupKey=alias_email).execute()
    if not g.get("name", "").startswith("Mailalias: "):
        raise HTTPException(status_code=403, detail="Not a managed mail‑alias")
    try:
        service.members().insert(groupKey=alias_email, body={"email": member_email, "role": "MEMBER"}).execute()
        members_result = service.members().list(groupKey=alias_email).execute()
        members = [m.get("email") for m in members_result.get("members", []) if m.get("email")]
        return AliasRead(alias=alias_email, members=members)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Add member failed: {e}")


@mail_alias_router.delete("/alias/{alias_email}/remove_member", response_model=AliasRead)
def remove_member(
    alias_email: str,
    member_email: EmailStr,
    service: Any = Depends(get_directory_service),
) -> AliasRead:
    g = service.groups().get(groupKey=alias_email).execute()
    if not g.get("name", "").startswith("Mailalias: "):
        raise HTTPException(status_code=403, detail="Not a managed mail‑alias")
    try:
        service.members().delete(groupKey=alias_email, memberKey=member_email).execute()
        members_result = service.members().list(groupKey=alias_email).execute()
        members = [m.get("email") for m in members_result.get("members", []) if m.get("email")]
        return AliasRead(alias=alias_email, members=members)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Remove member failed: {e}")


if __name__ == "__main__":

    alias: EmailStr = "test_alias@fsektionen.se"
    alias2: EmailStr = "test2_alias@fsektionen.se"

    create_alias(alias)

    add_member(alias_email=alias, member_email="benjamin_halasz@icloud.com")

    list_aliases()

    create_alias(alias2)

    list_aliases()

    add_member(alias_email=alias2, member_email="benjamin_halasz@icloud.com")

    delete_alias(alias_email=alias2)

    list_aliases()

    remove_member(alias_email=alias, member_email="benjamin_halasz@icloud.com")

    list_aliases()

    delete_alias(alias_email=alias)
