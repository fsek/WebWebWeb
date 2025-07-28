from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from google.oauth2 import service_account

# pyright: reportMissingTypeStubs=false
from googleapiclient.discovery import build  # type: ignore
from pydantic import EmailStr
from api_schemas.mail_alias_schema import AliasRead
import os

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS_PATH", "no_credentials.json")
ADMIN_EMAIL = os.getenv("GOOGLE_ADMIN_EMAIL", "admin@onlyworksinprod.com")
DOMAIN = ADMIN_EMAIL.split("@")[-1]

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
    "https://www.googleapis.com/auth/apps.groups.settings",
]

mail_alias_router = APIRouter()


def get_directory_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=ADMIN_EMAIL
    )
    return build("admin", "directory_v1", credentials=credentials)


def get_groups_settings_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=ADMIN_EMAIL
    )
    return build("groupssettings", "v1", credentials=credentials)


@mail_alias_router.post("/alias", response_model=AliasRead)
def create_alias(
    alias: EmailStr,
    directory_service=Depends(get_directory_service),
    settings_service=Depends(get_groups_settings_service),
):
    try:
        # Create group as alias
        directory_service.groups().insert(
            body={
                "email": alias,
                "name": f"Mailalias: {alias}",
            }
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Group (alias) creation failed: {e}")

    try:
        # Allow external senders
        settings_service.groups().patch(
            groupUniqueId=alias,
            body={"whoCanPostMessage": "ANYONE_CAN_POST", "allowExternalMembers": "true", "isArchived": "false"},
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Alias settings update failed: {e}")

    return Response(
        status_code=status.HTTP_201_CREATED,
    )


@mail_alias_router.get("/aliases", response_model=List[AliasRead])
def list_aliases(service=Depends(get_directory_service)):
    aliases: List[AliasRead] = []
    try:
        results = service.groups().list(domain=DOMAIN).execute()
        groups = results.get("groups", [])
        for group in groups:
            group_email = group["email"]
            try:
                members_result = service.members().list(groupKey=group_email).execute()
                members = [m["email"] for m in members_result.get("members", [])]
                aliases.append(AliasRead(alias=group_email, members=members))
            except:
                continue
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Listing aliases failed: {e}")
    return aliases


@mail_alias_router.delete("/alias/{alias_email}")
def delete_alias(alias_email: str, service=Depends(get_directory_service)):
    try:
        service.groups().delete(groupKey=alias_email).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete alias: {e}")
    return {"status": "deleted", "alias": alias_email}


@mail_alias_router.post("/alias/{alias_email}/add_member", response_model=AliasRead)
def add_member(alias_email: str, member_email: EmailStr, service=Depends(get_directory_service)):
    try:
        service.members().insert(groupKey=alias_email, body={"email": member_email, "role": "MEMBER"}).execute()
        members_result = service.members().list(groupKey=alias_email).execute()
        members = [m["email"] for m in members_result.get("members", [])]
        return AliasRead(alias=alias_email, members=members)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Add member failed: {e}")


@mail_alias_router.delete("/alias/{alias_email}/remove_member", response_model=AliasRead)
def remove_member(alias_email: str, member_email: EmailStr, service=Depends(get_directory_service)):
    try:
        service.members().delete(groupKey=alias_email, memberKey=member_email).execute()
        members_result = service.members().list(groupKey=alias_email).execute()
        members = [m["email"] for m in members_result.get("members", [])]
        return AliasRead(alias=alias_email, members=members)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Remove member failed: {e}")
