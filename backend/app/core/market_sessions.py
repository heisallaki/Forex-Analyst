from datetime import UTC, datetime

SESSION_WINDOWS_UTC = {
    "Sydney": (22, 7),
    "Tokyo": (0, 9),
    "London": (8, 17),
    "New York": (13, 22),
}


def _is_hour_in_window(hour: int, start: int, end: int) -> bool:
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


def get_active_sessions(now: datetime | None = None) -> list[str]:
    current = now or datetime.now(UTC)
    hour = current.astimezone(UTC).hour
    return [
        name
        for name, (start, end) in SESSION_WINDOWS_UTC.items()
        if _is_hour_in_window(hour, start, end)
    ]
