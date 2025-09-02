from fastapi import APIRouter, HTTPException, status
from api_schemas.candidate_schema import CandidatePostRead
from database import DB_dependency
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from db_models.user_model import User_DB
from user.permission import Permission
from api_schemas.election_schema import (
    ElectionRead,
    ElectionCreate,
    ElectionMemberRead,
    ElectionUpdate,
)
from typing import Annotated

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


@election_router.get(
    "/my-candidations/{election_id}", response_model=list[CandidatePostRead], dependencies=[Permission.member()]
)
def get_my_candidations(election_id: int, db: DB_dependency, me: Annotated[User_DB, Permission.member()]):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    candidations = [c.candidations for c in me.candidates if c.election_id == election_id]
    candidations = [c for sublist in candidations for c in sublist]

    candidations = [
        CandidatePostRead(post_id=c.election_post.post_id, election_post_id=c.election_post_id) for c in candidations
    ]

    return candidations


@election_router.post("/", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")])
def create_election(data: ElectionCreate, db: DB_dependency):
    if data.end_time_guild_meeting != None and data.end_time_guild_meeting < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")
    if data.end_time_middle_meeting != None and data.end_time_middle_meeting < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")
    if data.end_time_all < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")

    # Handle the posts
    post_ids = set(data.post_ids or [])

    existing_posts = db.query(Post_DB.id).filter(Post_DB.id.in_(post_ids)).all()
    existing_post_ids = {post.id for post in existing_posts}

    missing_post_ids = post_ids - existing_post_ids
    if missing_post_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post ids not found: {missing_post_ids}")

    election_posts = [ElectionPost_DB(post_id=post_id) for post_id in data.post_ids] if data.post_ids else []

    election = Election_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        start_time=data.start_time,
        end_time_guild_meeting=data.end_time_guild_meeting,
        end_time_middle_meeting=data.end_time_middle_meeting,
        end_time_all=data.end_time_all,
        description_sv=data.description_sv,
        description_en=data.description_en,
        election_posts=election_posts,
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
    if data.start_time is not None:
        if data.end_time_guild_meeting is not None and data.end_time_guild_meeting < data.start_time:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")
        if data.end_time_middle_meeting is not None and data.end_time_middle_meeting < data.start_time:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")
        if data.end_time_all is not None and data.end_time_all < data.start_time:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Starttime is after endtime")

    # Handle the posts
    post_ids = set(data.post_ids or [])

    existing_posts = db.query(Post_DB.id).filter(Post_DB.id.in_(post_ids)).all()
    existing_post_ids = {post.id for post in existing_posts}

    missing_post_ids = post_ids - existing_post_ids
    if missing_post_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post ids not found: {missing_post_ids}")

    election_posts = [ElectionPost_DB(post_id=post_id) for post_id in data.post_ids] if data.post_ids else []

    for var, value in vars(data).items():
        # This should remove all the posts if [] or None is passed as post_ids
        if var == "post_ids":
            election.election_posts = election_posts
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
