from calendar import c
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class BaseModel_DB(DeclarativeBase, MappedAsDataclass): #BaseModel_DB is a class that inherits from DeclarativeBase and MappedAsDataclass
    pass


class Car_DB(BaseModel_DB): #Car_DB is a class that inherits from BaseModel_DB
    __tablename__ = "car_table"
    
    # Integer value, makred as primary key. Every table need one primary key column.
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # Integer column of number of seats
    num_seats: Mapped[int] = mapped_column()
    
    # Integer column of milage
    milage: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_table.id"), default=None
    )

    user: Mapped[Optional["User_DB"]] = relationship(back_populates="cars" , init=False)




class User_DB(BaseModel_DB):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    user: Mapped[str] = mapped_column(String(250))

    cars: Mapped[list["Car_DB"]] = relationship(back_populates="user", init=False) #back_populates="user" is the name of the relationship in the other class


    




