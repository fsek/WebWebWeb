from pydantic import AliasPath, computed_field
from api_schemas.csv_schemas.base_csv_schema import BaseCsvSchema, CsvField
from helpers.types import DRINK_PACKAGES


class EventUserCsvSchema(BaseCsvSchema):
    __column_order__ = [
        "stil_id",
        "last_name",
        "first_name",
        "name",
        "email",
        "food_prefs",
        "drinkPackage",
        "group_name",
        "priority",
    ]

    first_name: str = CsvField("Förnamn", from_path=AliasPath("user", "first_name"))
    last_name: str = CsvField("Efternamn", from_path=AliasPath("user", "last_name"))
    stil_id: str | None = CsvField("Stil-ID", from_path=AliasPath("user", "stil_id"))
    email: str = CsvField("E-post", from_path=AliasPath("user", "email"))
    standard_food_preferences: list[str] | None = CsvField(
        from_path=AliasPath("user", "standard_food_preferences"), exclude=True
    )
    other_food_preferences: str | None = CsvField(from_path=AliasPath("user", "other_food_preferences"), exclude=True)
    drinkPackage: DRINK_PACKAGES = CsvField("Dryckespaket")
    group_name: str | None = CsvField("Grupp")
    priority: str = CsvField("Prioritet")

    @computed_field(alias="Namn", return_type=str)
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @computed_field(alias="Matpreferens", return_type=str)
    @property
    def food_prefs(self):
        res: list[str] = []
        if self.standard_food_preferences:
            res += self.standard_food_preferences
        if self.other_food_preferences:
            res.append(self.other_food_preferences)

        return ", ".join(res)
