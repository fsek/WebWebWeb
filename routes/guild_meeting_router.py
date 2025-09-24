from fastapi import APIRouter, HTTPException
from database import DB_dependency
from db_models.guild_meeting_model import GuildMeeting_DB
from api_schemas.guild_meeting_schema import GuildMeetingRead, GuildMeetingUpdate
from user.permission import Permission
from typing import Annotated


guild_meeting_router = APIRouter()


def create_empty_guild_meeting(db: DB_dependency) -> GuildMeeting_DB:
    """Create a new guild meeting record with empty/default values"""
    gm = GuildMeeting_DB(
        title_sv="",
        title_en="",
        date_description_sv="",
        date_description_en="",
        description_sv="",
        description_en="",
        is_active=True,
    )
    db.add(gm)
    db.commit()
    db.refresh(gm)
    return gm


def get_or_create_guild_meeting(db: DB_dependency, view_permission: bool) -> GuildMeeting_DB:
    """Get the guild meeting record, creating it if it doesn't exist"""
    gm = db.query(GuildMeeting_DB).filter_by(id=1).one_or_none()
    if gm is None:
        gm = create_empty_guild_meeting(db)
    if gm.is_active or view_permission:
        return gm
    else:
        raise HTTPException(status_code=403, detail="Guild meeting is not active.")


@guild_meeting_router.get("/", response_model=GuildMeetingRead)
def get_guild_meeting(db: DB_dependency, view_permission: Annotated[bool, Permission.check("view", "GuildMeeting")]):
    return get_or_create_guild_meeting(db, view_permission)


@guild_meeting_router.patch(
    "/",
    response_model=GuildMeetingRead,
    dependencies=[Permission.require("manage", "GuildMeeting")],
)
def update_guild_meeting(data: GuildMeetingUpdate, db: DB_dependency):
    gm = db.query(GuildMeeting_DB).filter_by(id=1).one_or_none()
    if gm is None:
        gm = create_empty_guild_meeting(db)

    for var, value in vars(data).items():
        if value is not None:
            setattr(gm, var, value)
    db.commit()
    return gm
