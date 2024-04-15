from datetime import datetime


def round_whole_minute(date: datetime):
    return date.replace(second=0, microsecond=0)
