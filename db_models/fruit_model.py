from typing import Optional
from db_models.base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped


class Fruit_DB(BaseModel_DB):
    __tablename__ = "fruit_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    color: Mapped[str] = mapped_column()

    price: Mapped[Optional[int]] = mapped_column()

    is_moldy: Mapped[bool] = mapped_column(init=False, default=False)
