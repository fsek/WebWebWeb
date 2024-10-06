from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from services.election_service import fix_election_read, fix_election_reads
from user.permission import Permission
from api_schemas.election_schema import ElectionPostRead, ElectionAddPosts, ElectionRead, ElectionCreate

election_router = APIRouter()


@election_router.get("/", response_model=list[ElectionRead], dependencies=[Permission.require("manage", "Election")])
def get_all_elections(db: DB_dependency):
    return fix_election_reads(db.query(Election_DB).all())


@election_router.get(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def get_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return fix_election_read(election)


@election_router.post("/", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")])
def create_election(data: ElectionCreate, db: DB_dependency):
    if data.end_time < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    election = Election_DB(
        title=data.title, start_time=data.start_time, end_time=data.end_time, description=data.description
    )
    db.add(election)
    db.commit()
    return fix_election_read(election)


@election_router.delete(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def delete_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(election)
    return fix_election_read(election)


@election_router.post(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def add_post_to_election(election_id: int, data: ElectionAddPosts, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")

    if not data.posts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No posts provided")

    post_ids = set(data.posts)

    existing_posts = db.query(Post_DB.id).filter(Post_DB.id.in_(post_ids)).all()
    existing_post_ids = {post.id for post in existing_posts}

    missing_post_ids = post_ids - existing_post_ids
    if missing_post_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Posts not found: {missing_post_ids}")

    existing_election_posts = (
        db.query(ElectionPost_DB.post_id)
        .filter(ElectionPost_DB.election_id == election_id, ElectionPost_DB.post_id.in_(post_ids))
        .all()
    )
    existing_election_post_ids = {ep.post_id for ep in existing_election_posts}

    new_post_ids = post_ids - existing_election_post_ids

    election_posts = [ElectionPost_DB(election_id=election_id, post_id=post_id) for post_id in new_post_ids]
    db.add_all(election_posts)
    db.commit()

    db.refresh(election)

    return fix_election_read(election)
