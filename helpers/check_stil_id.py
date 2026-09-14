import re


def check_stil_id(s: str) -> bool:
    if not len(s) == 10:
        return False
    pattern = r"^[a-z]{2}\d{4}[a-z]{2}-s$"
    return bool(re.fullmatch(pattern, s))
