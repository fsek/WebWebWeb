from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.election_model import Election_DB
from user.permission import Permission

election_router = APIRouter()


@election_router.get("/", response_model=[], dependencies=[Permission.require("manage", "Election")])
def get_all_elections(db: DB_dependency):
    return db.query(Election_DB).all()


@election_router.get("/{election_id}", response_model=[], dependencies=[Permission.require("manage", "Election")])
def get_election(election_id: int, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).first()
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return election
