from pydantic import AliasPath, computed_field
from api_schemas.csv_schemas.base_csv_schema import BaseCsvSchema, CsvField


class CandidatesCsvSchema(BaseCsvSchema):
    __column_order__ = ["stil_id", "last_name", "first_name", "name", "email", "post_name", "council_name"]

    first_name: str = CsvField("Förnamn", from_path=AliasPath("candidate", "user", "first_name"))
    last_name: str = CsvField("Efternamn", from_path=AliasPath("candidate", "user", "last_name"))
    stil_id: str | None = CsvField("Stil-ID", from_path=AliasPath("candidate", "user", "stil_id"))
    email: str = CsvField("E-postadress", from_path=AliasPath("candidate", "user", "email"))
    post_name: str = CsvField("Post", from_path=AliasPath("post", "name_sv"))
    council_name: str = CsvField("Utskott", from_path=AliasPath("post", "council", "name_sv"))

    @computed_field(alias="Namn", return_type=str)
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
