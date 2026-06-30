from fastapi import APIRouter, Body, HTTPException
from database import DB_dependency
from db_models.prereg_member_model import PreregMember_DB
from api_schemas.prereg_member_schema import (
    PreregMemberCreate,
    PreregMemberRead,
    PreregMemberUpdate,
)
from user.permission import Permission
from helpers.check_stil_id import check_stil_id
import phonenumbers

prereg_member_router = APIRouter()


def normalize_telephone_number(telephone_number: str | None) -> str | None:
    if telephone_number is None:
        return None

    return phonenumbers.format_number(
        phonenumbers.parse(str(telephone_number), None), phonenumbers.PhoneNumberFormat.E164
    )


def prereg_member_matches(member: PreregMember_DB, data: PreregMemberCreate | PreregMemberUpdate) -> bool:
    return (
        normalize_telephone_number(member.telephone_number) == normalize_telephone_number(data.telephone_number)
        and member.stil_id == data.stil_id
        and member.email == data.email
    )


def validate_identifiers(data: PreregMemberCreate | PreregMemberUpdate) -> bool:
    if data.stil_id:
        if not check_stil_id(data.stil_id):
            return False

    if data.email:
        if "@" not in data.email or "." not in data.email:
            return False

    return True


@prereg_member_router.get("/", response_model=list[PreregMemberRead], dependencies=[Permission.require("view", "User")])
def get_all_prereg_member_info(db: DB_dependency):
    all_prereg_members = db.query(PreregMember_DB).all()
    return all_prereg_members


@prereg_member_router.get(
    "/{prereg_member_id}", response_model=PreregMemberRead, dependencies=[Permission.require("view", "User")]
)
def get_prereg_member_info(prereg_member_id: int, db: DB_dependency):
    prereg_member = db.query(PreregMember_DB).filter(PreregMember_DB.prereg_member_id == prereg_member_id).one_or_none()
    if not prereg_member:
        raise HTTPException(404, detail="Prereg member not found")
    return prereg_member


@prereg_member_router.post("/", response_model=PreregMemberRead, dependencies=[Permission.require("manage", "User")])
def create_prereg_member(
    data: PreregMemberCreate,
    db: DB_dependency,
):
    if not (data.telephone_number or data.stil_id or data.email):
        raise HTTPException(
            400, detail="At least one identifier (telephone number, stil_id, or email) must be provided"
        )

    if not validate_identifiers(data):
        raise HTTPException(400, detail="Invalid identifier(s) provided")

    existing_prereg_member = next(
        (member for member in db.query(PreregMember_DB).all() if prereg_member_matches(member, data)),
        None,
    )
    if existing_prereg_member:
        raise HTTPException(400, detail="Prereg member with the exact same details already exists")
    prereg_member = PreregMember_DB(
        telephone_number=data.telephone_number,
        stil_id=data.stil_id,
        email=data.email,
    )
    db.add(prereg_member)
    db.commit()
    return prereg_member


@prereg_member_router.post(
    "/multiple",
    response_model=list[PreregMemberRead],
    dependencies=[Permission.require("manage", "User")],
)
def create_multiple_prereg_members(
    data: list[PreregMemberCreate],
    db: DB_dependency,
):
    prereg_members: list[PreregMember_DB] = []
    existing_prereg_members: list[PreregMember_DB] = []
    for member_data in data:
        if not (member_data.telephone_number or member_data.stil_id or member_data.email):
            raise HTTPException(
                400,
                detail="At least one identifier (telephone number, stil_id, or email) must be provided for all entries you want to add",
            )

        if not validate_identifiers(member_data):
            raise HTTPException(
                400,
                detail=f"One of the entries had an invalid identifier. At least one of the telephone number: {member_data.telephone_number}, stil_id: {member_data.stil_id}, or email: {member_data.email} is invalid",
            )

        existing_prereg_member = next(
            (member for member in db.query(PreregMember_DB).all() if prereg_member_matches(member, member_data)),
            None,
        )

        if existing_prereg_member:
            # There is already an entry with the exact same combination of identifiers.
            # Erroring here would be too strict
            existing_prereg_members.append(existing_prereg_member)
            continue

        prereg_member = PreregMember_DB(
            telephone_number=member_data.telephone_number,
            stil_id=member_data.stil_id,
            email=member_data.email,
        )
        db.add(prereg_member)
        prereg_members.append(prereg_member)

    if len(existing_prereg_members) >= 0 and len(existing_prereg_members) == len(data):
        raise HTTPException(400, detail="All prereg members already exist")

    db.commit()

    # Note: returns all existing prereg members that would collide unless they were skipped, not the newly created prereg members
    return existing_prereg_members


@prereg_member_router.patch(
    "/{prereg_member_id}", response_model=PreregMemberRead, dependencies=[Permission.require("manage", "User")]
)
def update_prereg_member(prereg_member_id: int, data: PreregMemberUpdate, db: DB_dependency):
    prereg_member = db.query(PreregMember_DB).filter(PreregMember_DB.prereg_member_id == prereg_member_id).one_or_none()
    if not prereg_member:
        raise HTTPException(404, detail="Prereg member not found")

    if not validate_identifiers(data):
        raise HTTPException(400, detail="Invalid identifier(s) provided")

    for var, value in vars(data).items():
        # Update the fields even if they are being set to None so they can be cleared
        setattr(prereg_member, var, value)

    if not (prereg_member.telephone_number or prereg_member.stil_id or prereg_member.email):
        db.rollback()
        raise HTTPException(
            400, detail="At least one identifier (telephone number, stil_id, or email) must be provided"
        )

    db.commit()
    return prereg_member


@prereg_member_router.delete(
    "/multiple",
    response_model=list[PreregMemberRead],
    dependencies=[Permission.require("manage", "User")],
)
def delete_multiple_prereg_members(
    db: DB_dependency,
    prereg_member_ids: list[int] = Body(...),
):
    prereg_members = db.query(PreregMember_DB).filter(PreregMember_DB.prereg_member_id.in_(prereg_member_ids)).all()
    if not prereg_members:
        raise HTTPException(404, detail="No prereg members found for the provided ids")
    if len(prereg_members) != len(prereg_member_ids):
        raise HTTPException(404, detail="Some prereg members not found for the provided ids")
    for member in prereg_members:
        db.delete(member)
    db.commit()
    return prereg_members


@prereg_member_router.delete(
    "/{prereg_member_id}", response_model=PreregMemberRead, dependencies=[Permission.require("manage", "User")]
)
def delete_prereg_member(prereg_member_id: int, db: DB_dependency):
    prereg_member = db.query(PreregMember_DB).filter(PreregMember_DB.prereg_member_id == prereg_member_id).one_or_none()
    if not prereg_member:
        raise HTTPException(404, detail="Prereg member not found")
    db.delete(prereg_member)
    db.commit()
    return prereg_member
