from datetime import UTC, datetime

_last_tick_at: datetime | None = None


def record_tick() -> None:
    global _last_tick_at
    _last_tick_at = datetime.now(UTC)


def get_last_tick_at() -> datetime | None:
    return _last_tick_at


def seconds_since_last_tick() -> float | None:
    if _last_tick_at is None:
        return None
    return (datetime.now(UTC) - _last_tick_at).total_seconds()
