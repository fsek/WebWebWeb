from typing import Annotated

from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field


class BaseCsvSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    __column_order__: Annotated[list[str] | None, Field(exclude=True)] = None


def CsvField(name: str | None = None, from_path: str | AliasPath | AliasChoices | None = None, exclude: bool = False):
    return Field(serialization_alias=name, validation_alias=from_path, exclude=exclude)
