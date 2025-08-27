from datetime import datetime, timezone


def now():
    """
    Returns the current date and time in ISO 8601 format.
    """

    return datetime.now(timezone.utc)
