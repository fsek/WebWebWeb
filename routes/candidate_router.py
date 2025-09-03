from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from api_schemas.candidate_schema import CandidateElectionCreate, CandidateRead, CandidatePostRead
from database import DB_dependency
from db_models.candidate_model import Candidate_DB
from db_models.candidate_post_model import Candidation_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.user_model import User_DB
from user.permission import Permission


candidate_router = APIRouter()


@candidate_router.get(
    "/{election_id}", response_model=list[CandidateRead], dependencies=[Permission.require("view", "Election")]
)
def get_all_candidates(election_id: int, db: DB_dependency):
    candidates = db.query(Candidate_DB).filter(Candidate_DB.election_id == election_id).all()

    return candidates


@candidate_router.get(
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


@candidate_router.post("/{election_id}", response_model=CandidateRead, dependencies=[Permission.member()])
def create_candidation(
    election_id: int,
    post_id: int,
    user_id: int,
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "Election")],
):

    if not manage_permission and user_id != me.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a candidation for this user.",
        )

    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Election does not exist",
        )

    candidate = (
        db.query(Candidate_DB)
        .filter(Candidate_DB.election_id == election_id, Candidate_DB.user_id == user_id)
        .one_or_none()
    )
    if candidate is None:
        candidate = Candidate_DB(election_id=election_id, user_id=user_id)
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


@candidate_router.delete("/{election_id}/candidate/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    election_id: int,
    user_id: int,
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "Election")],
):
    if user_id == me.id or manage_permission:
        candidate = (
            db.query(Candidate_DB)
            .filter(Candidate_DB.user_id == user_id, Candidate_DB.election_id == election_id)
            .one_or_none()
        )
        if candidate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found.",
            )

        db.delete(candidate)
        db.commit()

    return


@candidate_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidation(
    election_post_id: int,
    candidate_id: int,
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "Election")],
):
    if not manage_permission and not any(c.candidate_id == candidate_id for c in me.candidates):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this candidation.",
        )

    candidation = (
        db.query(Candidation_DB)
        .filter(Candidation_DB.election_post_id == election_post_id)
        .filter(Candidation_DB.candidate_id == candidate_id)
        .one_or_none()
    )

    if candidation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidation not found.",
        )

    db.delete(candidation)
    db.commit()

    return
