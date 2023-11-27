from fastapi import Depends, FastAPI
from database import get_db, engine
from sqlalchemy.orm import Session
from db_models import BaseModelDB
from schemas import BaseSchema

app = FastAPI()

BaseModelDB.metadata.create_all(engine)


class ParentRead(BaseSchema):
    id: int
    # parents: list["ChildRead"]
    # If we try returning a circular reference from a route we get recursion error


class ChildRead(BaseSchema):
    id: int
    parents: list[ParentRead]


class FamilyCreate(BaseSchema):
    # TODO replace pass and implement
    pass


@app.get("/make-family", response_model=ChildRead)
def make_family(family: FamilyCreate, db: Session = Depends(get_db)):
    # TODO create two parents and a child. Also make sure they're linked

    return


@app.get("/abandon-child/{child_id}", response_model=None)
def lose_child(child_id: int, db: Session = Depends(get_db)):
    # TODO delete a child

    # Do you also need to delete rows in the association table?

    return None
