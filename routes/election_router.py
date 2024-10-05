from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from user.permission import Permission
from api_schemas.election_schema import ElectionAddPosts, ElectionRead, ElectionCreate

election_router = APIRouter()


@election_router.get("/", response_model=list[ElectionRead], dependencies=[Permission.require("manage", "Election")])
def get_all_elections(db: DB_dependency):
    return db.query(Election_DB).all()


@election_router.get(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def get_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return election


@election_router.post("/", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")])
def create_election(data: ElectionCreate, db: DB_dependency):
    if data.end_time < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    election = Election_DB(
        title=data.title, start_time=data.start_time, end_time=data.end_time, description=data.description
    )
    db.add(election)
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
    return election


@election_router.post(
    "/{election_id}", response_model=ElectionRead, dependencies=[Permission.require("manage", "Election")]
)
def add_post_to_election(election_id: int, data: ElectionAddPosts, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    posts = db.query(Post_DB).all()

    for post in data.posts:
        i = 0
        for real_post in posts:
            if real_post.id == post:
                i = i + 1
        if i != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    election_posts:list[ElectionPost_DB] = []

    for post in data.posts:

