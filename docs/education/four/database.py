from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
    relationship,
)


class BaseModel_DB(DeclarativeBase, MappedAsDataclass):
    pass


class User_DB(BaseModel_DB):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    cars: Mapped[list["Car_DB"]] = relationship(back_populates="user", init=False)


class Car_DB(BaseModel_DB):
    __tablename__ = "car_table"

    # Integer value, makred as primary key. Every table need one primary key column.
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # String value, max length 250
    driver_name: Mapped[str] = mapped_column(String(250))

    # Integer column
    num_seats: Mapped[int] = mapped_column()

    # Integer column
    milage: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id"), default=None)

    user: Mapped[Optional["User_DB"]] = relationship(back_populates="cars", init=False)
