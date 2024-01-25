from datetime import datetime, timedelta
from fastapi import HTTPException, status


def force_utc(datetime: datetime):
    zero_dt = timedelta(0)

    # We want to talk in UTC times to be clear and avoid timezone confusion.
    # This will force client to give us a timestamp in UTC
    if datetime.utcoffset() != zero_dt:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Datetimes must be UTC")


def round_whole_minute(date: datetime):
    return date.replace(second=0, microsecond=0)
