from fastapi import APIRouter, HTTPException, status

from api_schemas.nomination_schema import NominationCreate, NominationRead
from database import DB_dependency
from db_models.nomination_model import Nominee_DB
from db_models.election_model import Election_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.nomination_post_model import Nomination_DB
from user.permission import Permission


nomination_router = APIRouter()


@nomination_router.get("/{election_id}", response_model=list[NominationRead], dependencies=[Permission.member()])
def get_all_nominations(election_id: int, db: DB_dependency):
    nominations = db.query(Nominee_DB).filter(Nominee_DB.election_id == election_id).all()

    return nominations


@nomination_router.post("/{election_id}", response_model=NominationRead, dependencies=[Permission.member()])
def create_nomination(election_id: int, post_id: int, data: NominationCreate, db: DB_dependency):
    election = db.query(Election_DB).filter(Election_DB.election_id == election_id).one_or_none()
    if election is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election does not exist")

    nominee = (
        db.query(Nominee_DB).filter(Nominee_DB.election_id == election_id, Nominee_DB.mail == data.mail).one_or_none()
    )
    if nominee is None:
        nominee = Nominee_DB(election_id=election_id, name=data.name, mail=data.mail, motivation=data.motivation)
        db.add(nominee)
        db.commit()
        db.refresh(nominee)

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

    existing_nomination = (
        db.query(Nomination_DB)
        .filter(Nomination_DB.nominee_id == nominee.nominee_id, Nomination_DB.election_post_id == post_id)
        .one_or_none()
    )

    if existing_nomination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This nominee is already associated with the specified post.",
        )
    new_nomination = Nomination_DB(nominee_id=nominee.nominee_id, election_post_id=post_id)
    db.add(new_nomination)
    db.commit()
    db.refresh(new_nomination)
    return nominee
