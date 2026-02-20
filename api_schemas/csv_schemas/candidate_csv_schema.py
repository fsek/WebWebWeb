from pydantic import computed_field
from api_schemas.csv_schemas.base_csv_schema import BaseCsvSchema, CsvField


class CandidatesCsvSchema(BaseCsvSchema):
    __column_order__ = ["stil_id", "name", "email", "post_name", "council_name"]

    first_name: str = CsvField("Förnamn", exclude=True)
    last_name: str = CsvField("Efternamn", exclude=True)
    stil_id: str | None = CsvField("Stil-ID")
    email: str = CsvField("E-postadress")
    post_name: str = CsvField("Post")
    council_name: str = CsvField("Utskott")

    @computed_field(alias="Namn", return_type=str)
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
