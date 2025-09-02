from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from api_schemas.candidate_schema import CandidateElectionCreate, CandidateRead
from database import DB_dependency
from db_models.candidate_model import Candidate_DB
from db_models.candidate_post_model import Candidation_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.user_model import User_DB
from user.permission import Permission


candidate_router = APIRouter()


@candidate_router.get("/{election_id}", response_model=list[CandidateRead], dependencies=[Permission.member()])
def get_all_candidations(election_id: int, db: DB_dependency):
    # .join(User_DB)
    candidations = db.query(Candidate_DB).join(User_DB).filter(Candidate_DB.election_id == election_id).all()

    return candidations


@candidate_router.post("/many/{election_id}", response_model=CandidateRead, dependencies=[Permission.member()])
def create_candidations(
    election_id: int, data: CandidateElectionCreate, me: Annotated[User_DB, Permission.member()], db: DB_dependency
):
    candidate = (
        db.query(Candidate_DB)
        .filter(Candidate_DB.election_id == election_id, Candidate_DB.user_id == me.id)
        .one_or_none()
    )

    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election does not exist")

    if candidate is None:
        candidate = Candidate_DB(election_id=election_id, user_id=me.id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    election_posts = db.query(ElectionPost_DB).filter(ElectionPost_DB.election_id == election_id).all()
    post_id_to_election_post_id = {ep.post_id: ep.election_post_id for ep in election_posts}

    invalid_posts = [post for post in data.post_ids if post not in post_id_to_election_post_id]
    if invalid_posts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid post IDs provided: {invalid_posts}"
        )

    valid_election_post_ids = [post_id_to_election_post_id[post] for post in data.post_ids]

    existing_candidations = (
        db.query(Candidation_DB.election_post_id)
        .filter(Candidation_DB.candidate_id == candidate.candidate_id)
        .filter(Candidation_DB.election_post_id.in_(valid_election_post_ids))
        .all()
    )
    existing_election_post_ids = {cp.election_post_id for cp in existing_candidations}

    new_election_post_ids = set(valid_election_post_ids) - existing_election_post_ids

    if not new_election_post_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All provided posts are already associated with the candidate.",
        )

    candidations = [
        Candidation_DB(candidate_id=candidate.candidate_id, election_post_id=ep_id, election_id=election_id)
        for ep_id in new_election_post_ids
    ]

    db.add_all(candidations)
    db.commit()

    return candidate


@candidate_router.post("/{election_id}", response_model=CandidateRead, dependencies=[Permission.member()])
def create_candidation(election_id: int, post_id: int, me: Annotated[User_DB, Permission.member()], db: DB_dependency):

    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Election does not exist",
        )

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

    election_post = (
        db.query(ElectionPost_DB)
        .filter(ElectionPost_DB.election_id == election_id, ElectionPost_DB.post_id == post_id)
        .one_or_none()
    )
    if election_post is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid post_id ({post_id}) for this election.",
        )

    existing_candidation = (
        db.query(Candidation_DB)
        .filter(
            Candidation_DB.candidate_id == candidate.candidate_id,
            Candidation_DB.election_post_id == election_post.election_post_id,
        )
        .one_or_none()
    )
    if existing_candidation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This candidate is already associated with the specified post.",
        )

    new_candidation = Candidation_DB(
        candidate_id=candidate.candidate_id, election_post_id=election_post.election_post_id, election_id=election_id
    )
    db.add(new_candidation)
    db.commit()

    return candidate
