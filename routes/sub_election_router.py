from fastapi import APIRouter, HTTPException, status
from db_models.candidate_model import Candidate_DB
from database import DB_dependency
from db_models.sub_election_model import SubElection_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from user.permission import Permission
from api_schemas.sub_election_schema import (
    SubElectionRead,
    SubElectionCreate,
    SubElectionUpdate,
    MovePostRequest,
)
from typing import List

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

    # Check if any of the posts are already assigned to another sub-election in the same election
    if post_ids:
        assigned_posts = (
            db.query(ElectionPost_DB.post_id)
            .join(SubElection_DB)
            .filter(SubElection_DB.election_id == data.election_id)
            .filter(ElectionPost_DB.post_id.in_(post_ids))
            .all()
        )
        assigned_post_ids = {post.post_id for post in assigned_posts}
        if assigned_post_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Post ids already assigned to another sub-election in the same election: {assigned_post_ids}",
            )

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

    # Check if any of the posts are already assigned to another sub-election in the same election
    if post_ids:
        assigned_posts = (
            db.query(ElectionPost_DB.post_id)
            .join(SubElection_DB)
            .filter(SubElection_DB.election_id == sub_election.election_id)
            .filter(SubElection_DB.sub_election_id != sub_election.sub_election_id)
            .filter(ElectionPost_DB.post_id.in_(post_ids))
            .all()
        )
        assigned_post_ids = {post.post_id for post in assigned_posts}
        if assigned_post_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Post ids already assigned to another sub-election in the same election: {assigned_post_ids}",
            )

    new_election_posts = [ElectionPost_DB(post_id=post_id) for post_id in data.post_ids] if data.post_ids else []

    # We want to keep the old posts, with all their data, if they are not removed
    election_posts: List[ElectionPost_DB] = []
    for new_post in new_election_posts:
        existing_post = next((ep for ep in sub_election.election_posts if ep.post_id == new_post.post_id), None)
        if existing_post:
            election_posts.append(existing_post)
        else:
            election_posts.append(new_post)

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


@sub_election_router.patch(
    "/{sub_election_id}/move-election-post",
    response_model=SubElectionRead,
    dependencies=[Permission.require("manage", "Election")],
)
def move_election_post(sub_election_id: int, data: MovePostRequest, db: DB_dependency):
    sub_election = db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == sub_election_id).one_or_none()
    if sub_election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    election_post = (
        db.query(ElectionPost_DB)
        .filter(ElectionPost_DB.election_post_id == data.election_post_id)
        .filter(ElectionPost_DB.sub_election_id == sub_election_id)
        .one_or_none()
    )
    if election_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Election post not found in this sub-election"
        )

    new_sub_election = (
        db.query(SubElection_DB).filter(SubElection_DB.sub_election_id == data.new_sub_election_id).one_or_none()
    )
    if new_sub_election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New sub-election not found")

    if new_sub_election.election_id != sub_election.election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="New sub-election is not in the same election"
        )

    if new_sub_election.sub_election_id == sub_election.sub_election_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You are trying to move to the same sub-election"
        )

    # Check if the post is already assigned to the new sub-election
    existing_post = (
        db.query(ElectionPost_DB)
        .filter(ElectionPost_DB.sub_election_id == new_sub_election.sub_election_id)
        .filter(ElectionPost_DB.post_id == election_post.post_id)
        .one_or_none()
    )
    if existing_post is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Post is already assigned to the new sub-election"
        )

    # Move the post to the new sub-election
    election_post.sub_election = new_sub_election

    # Update all the candidations to point to the new sub-election
    for candidation in election_post.candidations:
        candidation.sub_election = new_sub_election

    # Update all the nominations to point to the new sub-election
    for nomination in election_post.nominations:
        nomination.sub_election = new_sub_election

    # Add/update candidates on the new sub-election
    for candidate in sub_election.candidates:
        if election_post in candidate.election_posts:
            existing_candidate = (
                db.query(Candidate_DB)
                .filter(Candidate_DB.sub_election_id == new_sub_election.sub_election_id)
                .filter(Candidate_DB.user_id == candidate.user_id)
                .one_or_none()
            )
            if existing_candidate is None:
                candidate.sub_election = new_sub_election
                db.add(candidate)
            else:
                if election_post not in existing_candidate.election_posts:
                    existing_candidate.election_posts.append(election_post)

    # Update all candidates on the current sub-election to remove the election post
    for candidate in sub_election.candidates:
        if election_post in candidate.election_posts and len(candidate.election_posts) == 1:
            candidate.election_posts.remove(election_post)
            # Lets remove the candidate if they have no more election posts
            db.delete(candidate)
        elif election_post in candidate.election_posts:
            candidate.election_posts.remove(election_post)

    db.commit()
    return new_sub_election
