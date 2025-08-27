from datetime import datetime, timedelta


def datetime_from_now(days: int) -> datetime:
    """
    Get a datetime object representing the date and time
    a given number of days from now.

    Args:
        days (int): Number of days from now (can be negative for past dates).

    Returns:
        datetime: The calculated datetime.
    """
    return datetime.now() + timedelta(days=days)
