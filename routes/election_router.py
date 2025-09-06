from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.election_model import Election_DB
from user.permission import Permission
from api_schemas.election_schema import (
    ElectionRead,
    ElectionCreate,
    ElectionMemberRead,
    ElectionUpdate,
    ElectionPopulate,
)
from services.election_service import service_populate_election

election_router = APIRouter()


@election_router.get("/", response_model=list[ElectionRead], dependencies=[Permission.require("view", "Election")])
def get_all_elections(db: DB_dependency):
    return db.query(Election_DB).all()


@election_router.get(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("view", "Election")]
)
def get_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return election


@election_router.get("/member/", response_model=list[ElectionMemberRead], dependencies=[Permission.member()])
def get_all_elections_member(db: DB_dependency):
    return db.query(Election_DB).all()


@election_router.get("/member/{election_id}", response_model=ElectionMemberRead, dependencies=[Permission.member()])
def get_election_member(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return election


@election_router.post("/", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")])
def create_election(data: ElectionCreate, db: DB_dependency):

    existing_visible_elections = db.query(Election_DB).filter(Election_DB.visible == True).all()
    if data.visible and len(existing_visible_elections) > 1:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Only one election can be visible at a time. Something has gone wrong before this request.",
        )
    if data.visible and len(existing_visible_elections) == 1:
        existing_visible_elections[0].visible = False
        db.commit()

    election = Election_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        start_time=data.start_time,
        description_sv=data.description_sv,
        description_en=data.description_en,
        visible=data.visible,
    )
    db.add(election)
    db.commit()
    return election


@election_router.patch(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def update_election(election_id: int, data: ElectionUpdate, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    start = None
    earliest_close = None
    start = data.start_time if data.start_time is not None else election.start_time

    earliest_close = min([se.end_time for se in election.sub_elections or []], default=None)
    if earliest_close and earliest_close < start:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Earliest close time for the subelections is before start time"
        )

    existing_visible_elections = db.query(Election_DB).filter(Election_DB.visible == True).all()
    if data.visible and len(existing_visible_elections) > 1:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Only one election can be visible at a time. Something has gone wrong before this request.",
        )
    if data.visible and len(existing_visible_elections) == 1:
        existing_visible_elections[0].visible = False
        db.commit()

    for var, value in vars(data).items():
        if value is not None:
            setattr(election, var, value)

    db.commit()
    return election


@election_router.delete(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def delete_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(election)
    db.commit()
    return election


@election_router.post(
    "/{election_id}/populate", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def populate_election(election_id: int, data: ElectionPopulate, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    service_populate_election(db, election, data)
    db.refresh(election)
    return election
