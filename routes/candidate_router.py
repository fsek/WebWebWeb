from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from api_schemas.candidate_schema import CandidateRead
from database import DB_dependency
from db_models.candidate_model import Candidate_DB
from db_models.candidate_post_model import CandidatePost_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.user_model import User_DB
from user.permission import Permission


candidate_router = APIRouter()


@candidate_router.get("/{election_id}", response_model=list[CandidateRead], dependencies=[Permission.member()])
def get_all_candidations(election_id: int, db: DB_dependency):
    candidations = db.query(Candidate_DB).filter(Candidate_DB.election_id == election_id).all()

    return candidations


# @candidate_router.post("/{election_id}", response_model=CandidateRead, dependencies=[Permission.member()])
# def create_candidation(election_id: int, posts: list[int], me: Annotated[User_DB, Permission.member()], db: DB_dependency):
#     candidate = (
#         db.query(Candidate_DB)
#         .filter(Candidate_DB.election_id == election_id, Candidate_DB.user_id == me.id)
#         .one_or_none()
#     )
#     if candidate is None:
#         candidate = Candidate_DB(election_id=election_id, user_id=me.id)
#         db.add(candidate)
#         db.commit()

#     election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()

#     if election is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election does not exist")

#     election_posts = db.query(ElectionPost_DB).filter(ElectionPost_DB.election_id == election_id).all()

#     existing_election_post_ids = {ep.post_id for ep in election_posts}

#     candidations:list[CandidatePost_DB] = [if existing_election_post_ids.contains(post) then CandidatePost_DB(candidate_id=candidate.candidate_id, candidate=candidate, election_post_id=election. ) for post in posts]


@candidate_router.post("/{election_id}", response_model=CandidateRead, dependencies=[Permission.member()])
def create_candidation(
    election_id: int, posts: list[int], me: Annotated[User_DB, Permission.member()], db: DB_dependency
):
    candidate = (
        db.query(Candidate_DB)
        .filter(Candidate_DB.election_id == election_id, Candidate_DB.user_id == me.id)
        .one_or_none()
    )

    if candidate is None:
        candidate = Candidate_DB(election_id=election_id, user_id=me.id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election does not exist")

    election_posts = db.query(ElectionPost_DB).filter(ElectionPost_DB.election_id == election_id).all()
    existing_election_post_ids = {ep.election_post_id for ep in election_posts}

    invalid_posts = set(posts) - existing_election_post_ids
    if invalid_posts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid post IDs provided: {invalid_posts}"
        )

    candidations = [  # MUST BE FIXED BEFORE ACCEPTED
        CandidatePost_DB(candidate_id=candidate.candidate_id, election_post_id=post)
        for post in posts
        if post in existing_election_post_ids
    ]

    db.add_all(candidations)
    db.commit()

    return candidate
