from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column


"""
Example use on a DB model:
    class MyModel(BaseModel_DB):
        ...
        created_at: Mapped[datetime] = created_at_column()
        last_modified: Mapped[datetime] = latest_modified_column()

"""


# The with these we need not manually set created and modified dates.
def created_at_column():
    return mapped_column(insert_default=datetime.now(timezone.utc), init=False)


def latest_modified_column():
    return mapped_column(onupdate=datetime.now(timezone.utc), init=False)
