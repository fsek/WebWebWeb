from io import StringIO
from typing import Generic, TypeVar

from fastapi.responses import StreamingResponse
import pandas as pd

from api_schemas.csv_schemas.base_csv_schema import BaseCsvSchema


T = TypeVar("T", bound=BaseCsvSchema)


class CsvResponseFactory(Generic[T]):
    def __init__(self) -> None:
        self.__columns: dict[str, list[str]] = {}
        self.__length = 0

    def append(self, row: T) -> None:
        if self.__length == 0:
            self.__pre_append_first(row)

        dump = row.model_dump(by_alias=True)
        for k, v in dump.items():
            self.__columns[k].append(str(v))

        self.__length += 1

    def __pre_append_first(self, row: T) -> None:
        model_fields = {
            k: v.serialization_alias or v.alias or k
            for k, v in filter(lambda t: not t[1].exclude, row.model_fields.items())
        }
        model_computed_fields = {k: v.alias or k for k, v in row.model_computed_fields.items()}
        mappings = {**model_fields, **model_computed_fields}

        order = row.__column_order__
        if not order:
            order = list(mappings.keys())

        for c in order:
            self.__columns[mappings[c]] = []

    def to_csv(self) -> StringIO:
        df = pd.DataFrame(data=self.__columns)
        csv_file = StringIO()
        df.to_csv(csv_file, index=False)
        return csv_file

    def to_response(self, filename: str = "data.csv") -> StreamingResponse:
        csv_file = self.to_csv()
        response = StreamingResponse(iter([csv_file.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename={filename}"
        return response
