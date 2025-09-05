from fastapi import APIRouter, HTTPException, status

from api_schemas.nomination_schema import NominationRead, NominationCreate
from database import DB_dependency
from db_models.nomination_model import Nomination_DB
from db_models.sub_election_model import SubElection_DB
from db_models.election_post_model import ElectionPost_DB
from user.permission import Permission

nomination_router = APIRouter()


@nomination_router.get(
    "/election/{election_id}",
    response_model=list[NominationRead],
    dependencies=[Permission.require("view", "Election")],
)
def get_all_election_nominations(election_id: int, db: DB_dependency):
    sub_elections = db.query(SubElection_DB).filter(SubElection_DB.election_id == election_id).all()
    nominations = (
        db.query(Nomination_DB)
        .filter(Nomination_DB.sub_election_id.in_([se.sub_election_id for se in sub_elections]))
        .all()
    )
    return nominations


@nomination_router.get(
    "/sub-election/{sub_election_id}",
    response_model=list[NominationRead],
    dependencies=[Permission.require("view", "Election")],
)
def get_all_sub_election_nominations(sub_election_id: int, db: DB_dependency):
    nominations = db.query(Nomination_DB).filter(Nomination_DB.sub_election_id == sub_election_id).all()
    return nominations


@nomination_router.post("/{sub_election_id}", status_code=status.HTTP_201_CREATED, dependencies=[Permission.member()])
def create_nomination(sub_election_id: int, nomination: NominationCreate, db: DB_dependency):
    sub_election = db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == sub_election_id).one_or_none()
    if sub_election is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sub-election does not exist",
        )

    election_post = (
        db.query(ElectionPost_DB)
        .filter(
            ElectionPost_DB.election_post_id == nomination.election_post_id,
            ElectionPost_DB.sub_election_id == sub_election_id,
        )
        .one_or_none()
    )
    if election_post is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid election_post_id for this election.",
        )

    new_nomination = Nomination_DB(
        sub_election_id=sub_election_id,
        nominee_name=nomination.nominee_name,
        nominee_email=nomination.nominee_email,
        motivation=nomination.motivation,
        election_post_id=nomination.election_post_id,
    )
    db.add(new_nomination)
    db.commit()
    return


@nomination_router.delete(
    "/{nomination_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Permission.require("manage", "Election")]
)
def delete_nomination(nomination_id: int, db: DB_dependency):
    nomination = db.query(Nomination_DB).filter(Nomination_DB.nomination_id == nomination_id).one_or_none()
    if nomination is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nomination not found.",
        )
    db.delete(nomination)
    db.commit()
    return
