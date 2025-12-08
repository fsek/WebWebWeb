from fastapi import APIRouter, HTTPException, status
from sqlalchemy import and_, or_
from api_schemas.tool_schema import ToolCreate, ToolRead, ToolUpdate
from db_models.tool_model import Tool_DB
from user.permission import Permission
from database import DB_dependency


tool_router = APIRouter()


@tool_router.post("/", response_model=ToolRead, dependencies=[Permission.require("manage", "Tools")])
def create_tool(data: ToolCreate, db: DB_dependency):
    tool = db.query(Tool_DB).filter(Tool_DB.name_sv == data.name_sv).one_or_none()
    if tool is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is already a tool with that swedish name")
    tool = db.query(Tool_DB).filter(Tool_DB.name_en == data.name_en).one_or_none()
    if tool is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is already a tool with that english name")

    if data.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Amount must be positive")

    tool = Tool_DB(
        name_sv=data.name_sv,
        name_en=data.name_en,
        amount=data.amount,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(tool)
    db.commit()
    return tool


@tool_router.get("/", response_model=list[ToolRead], dependencies=[Permission.require("view", "Tools")])
def get_all_tools(db: DB_dependency):
    return db.query(Tool_DB).all()


@tool_router.get("/{tool_id}", response_model=ToolRead, dependencies=[Permission.require("view", "Tools")])
def get_tool(tool_id: int, db: DB_dependency):
    tool = db.query(Tool_DB).filter_by(id=tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, detail="Tool not found")
    return tool


@tool_router.patch(
    "/update_tool/{tool_id}", response_model=ToolRead, dependencies=[Permission.require("manage", "Tools")]
)
def update_tool(tool_id: int, data: ToolUpdate, db: DB_dependency):

    tool = db.query(Tool_DB).filter_by(id=tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, detail="Tool not found")

    conflicting_tool = (
        db.query(Tool_DB).filter(and_(Tool_DB.id != tool_id, Tool_DB.name_sv == data.name_sv)).one_or_none()
    )
    if conflicting_tool is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is another tool with that swedish name")
    conflicting_tool = (
        db.query(Tool_DB).filter(and_(Tool_DB.id != tool_id, Tool_DB.name_en == data.name_en)).one_or_none()
    )
    if conflicting_tool is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "There is another tool with that english name")

    if data.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Amount must be positive")

    for var, value in vars(data).items():
        setattr(tool, var, value) if value is not None else None

    db.commit()

    return tool


@tool_router.delete("/{tool_id}", response_model=ToolRead, dependencies=[Permission.require("manage", "Tools")])
def delete_tool(tool_id: int, db: DB_dependency):
    tool = db.query(Tool_DB).filter_by(id=tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, detail="Tool not found")
    db.delete(tool)
    db.commit()
    return tool
