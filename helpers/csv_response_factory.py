from io import StringIO
from typing import Generic, TypeVar

from fastapi.responses import StreamingResponse
import pandas as pd

from api_schemas.csv_schemas.base_csv_schema import BaseCsvSchema


T = TypeVar("T", bound=BaseCsvSchema)


class CsvResponseFactory(Generic[T]):
    def __init__(self, none_str: str = "") -> None:
        self.__columns: dict[str, list[str]] = {}
        self.__headers_initialized = False
        self.none_str = none_str

    def append(self, row: T) -> None:
        if not self.__headers_initialized:
            self.__initialize_headers(row)

        dump = row.model_dump(by_alias=True)
        for k in self.__columns.keys():
            self.__columns[k].append(str(dump[k] or self.none_str))

    def __initialize_headers(self, row: T) -> None:
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

        self.__headers_initialized = True

    def to_csv(self) -> StringIO:
        df = pd.DataFrame(data=self.__columns)
        csv_file = StringIO()
        df.to_csv(csv_file, index=False)
        return csv_file

    def to_response(self, filename: str = "data.csv") -> StreamingResponse:
        csv_file = self.to_csv()
        response = StreamingResponse(iter([csv_file.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
