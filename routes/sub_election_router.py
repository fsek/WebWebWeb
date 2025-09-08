from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.sub_election_model import SubElection_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from user.permission import Permission
from api_schemas.sub_election_schema import (
    SubElectionRead,
    SubElectionCreate,
    SubElectionMemberRead,
    SubElectionUpdate,
)

sub_election_router = APIRouter()


@sub_election_router.get(
    "/{sub_election_id}", response_model=SubElectionRead, dependencies=[Permission.require("view", "Election")]
)
def get_sub_election(sub_election_id: int, db: DB_dependency):
    sub_election = db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == sub_election_id).one_or_none()
    if sub_election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return sub_election


@sub_election_router.post("/", response_model=SubElectionRead, dependencies=[Permission.require("manage", "Election")])
def create_sub_election(data: SubElectionCreate, db: DB_dependency):
    # Find the election
    election = db.query(Election_DB).filter(Election_DB.election_id == data.election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    start_time = election.start_time

    end_time = data.end_time
    if end_time < start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "End time is before election start time")

    # Handle the posts
    post_ids = set(data.post_ids or [])

    existing_posts = db.query(Post_DB.id).filter(Post_DB.id.in_(post_ids)).all()
    existing_post_ids = {post.id for post in existing_posts}

    missing_post_ids = post_ids - existing_post_ids
    if missing_post_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Post ids not found: {missing_post_ids}")

    election_posts = [ElectionPost_DB(post_id=post_id) for post_id in data.post_ids] if data.post_ids else []

    sub_election = SubElection_DB(
        election_id=data.election_id,
        title_sv=data.title_sv,
        title_en=data.title_en,
        end_time=data.end_time,
        election_posts=election_posts,
    )
    db.add(sub_election)
    db.commit()
    return sub_election


@sub_election_router.patch(
    "/{sub_election_id}", response_model=SubElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def update_sub_election(sub_election_id: int, data: SubElectionUpdate, db: DB_dependency):
    sub_election = db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == sub_election_id).one_or_none()
    if sub_election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    election = sub_election.election

    start_time = election.start_time
    end_time = data.end_time if data.end_time is not None else sub_election.end_time
    if end_time < start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "End time is before election start time")

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
            sub_election.election_posts = election_posts
        elif value is not None:
            setattr(sub_election, var, value)

    db.commit()
    return sub_election


@sub_election_router.delete(
    "/{sub_election_id}", response_model=SubElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def delete_sub_election(sub_election_id: int, db: DB_dependency):
    sub_election = db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == sub_election_id).one_or_none()
    if sub_election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(sub_election)
    db.commit()
    return sub_election
