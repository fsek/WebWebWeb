import os
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, status

from api_schemas.moose_game_schema import MooseGameRead
from user.permission import Permission
from database import DB_dependency
from db_models.user_model import User_DB

MOOSE_GAME_SECRET = os.getenv("MOOSE_GAME_TOKEN")

moose_game_router = APIRouter()


@moose_game_router.post("/{score}")
def update_mouse_game_score(
    score: int, me: Annotated[User_DB, Permission.member()], request: Request, db: DB_dependency
):
    token = request.headers.get("moose-game-token")
    if MOOSE_GAME_SECRET != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Moose-game-token",
        )

    if me.moose_game_score == -1:
        raise HTTPException(status_code=status.WS_1008_POLICY_VIOLATION, detail="You have been a naughty boy")

    if me.moose_game_score > score:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Not a personal highscore")

    me.moose_game_score = score
    db.commit()


@moose_game_router.get("/", response_model=list[MooseGameRead], dependencies=[Permission.member()])
def get_all_scores(db: DB_dependency):
    users = (
        db.query(User_DB)
        .filter(User_DB.moose_game_score != -1)
        .filter(User_DB.moose_game_name != "")
        .order_by(User_DB.moose_game_score)
        .all()
    )
    return users


@moose_game_router.delete("/{user_id}", dependencies=[Permission.require("manage", "Moosegame")])
def remove_mouse_game_score(user_id: int, db: DB_dependency):
    user = db.query(User_DB).get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user.moose_game_score = -1
    db.commit()
