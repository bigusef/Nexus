"""Parser utilities for various data types"""

import re
from datetime import timedelta
from typing import Annotated

from pydantic import BeforeValidator


def parse_timedelta(value: str | timedelta) -> timedelta:
    """
    Parse timedelta from string format.

    Supported formats:
    - "30s" or "30sec" -> 30 seconds
    - "5m" or "5min" -> 5 minutes
    - "2h" or "2hr" -> 2 hours
    - "1d" or "1day" -> 1 day

    Args:
        value: String in format like "3m" or timedelta object

    Returns:
        timedelta object

    Raises:
        ValueError: If format is invalid

    Examples:
        >>> parse_timedelta("3m")
        timedelta(minutes=3)
        >>> parse_timedelta("30s")
        timedelta(seconds=30)
        >>> parse_timedelta("2h")
        timedelta(hours=2)
        >>> parse_timedelta("7d")
        timedelta(days=7)
    """
    if isinstance(value, timedelta):
        return value

    # Regex pattern to match number and unit
    pattern = r"^(\d+)(s|sec|m|min|h|hr|d|day)$"
    match = re.match(pattern, value.lower().strip())

    if not match:
        raise ValueError(f"Invalid timedelta format: {value}. Use formats like '30s', '5m', '2h', '1d'")

    amount = int(match.group(1))
    unit = match.group(2)

    # Convert to timedelta based on unit
    if unit in ("s", "sec"):
        return timedelta(seconds=amount)
    elif unit in ("m", "min"):
        return timedelta(minutes=amount)
    elif unit in ("h", "hr"):
        return timedelta(hours=amount)
    elif unit in ("d", "day"):
        return timedelta(days=amount)

    raise ValueError(f"Unknown time unit: {unit}")


# Type alias for timedelta fields parsed from strings (for use with Pydantic)
TimeDeltaStr = Annotated[timedelta, BeforeValidator(parse_timedelta)]
