"""Utility functions for services using UWS."""

from __future__ import annotations

from datetime import datetime, timezone


def isodatetime(timestamp: datetime) -> str:
    """Format a timestamp in UTC in the expected UWS ISO date format."""
    assert timestamp.tzinfo in (None, timezone.utc)
    return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_isodatetime(time_string: str) -> datetime | None:
    """Parse a string in the UWS ISO date format.

    Returns
    -------
    datetime.datetime or None
        The corresponding `datetime.datetime` or `None` if the string is
        invalid.
    """
    if not time_string.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(time_string[:-1] + "+00:00")
    except Exception:
        return None
