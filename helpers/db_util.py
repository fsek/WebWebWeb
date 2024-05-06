from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column

"""
Example use on a DB model:
    class MyModel(BaseModel_DB):
        ...
        created_at: Mapped[datetime] = created_at_column()
        last_modified: Mapped[datetime] = latest_modified_column()

"""
get_now_utc = lambda: datetime.now(timezone.utc) # note we gotta pass a function to insert_default, not a datetime value

# The with these we need not manually set created and modified dates.
def created_at_column():
    return mapped_column(insert_default=get_now_utc, init=False)


def latest_modified_column():
    return mapped_column(insert_default=get_now_utc,onupdate=get_now_utc, init=False)
