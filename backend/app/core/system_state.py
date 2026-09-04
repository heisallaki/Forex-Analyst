from datetime import datetime, timezone

_last_tick_at: datetime | None = None


def record_tick() -> None:
    global _last_tick_at
    _last_tick_at = datetime.now(timezone.utc)


def get_last_tick_at() -> datetime | None:
    return _last_tick_at


def seconds_since_last_tick() -> float | None:
    if _last_tick_at is None:
        return None
    return (datetime.now(timezone.utc) - _last_tick_at).total_seconds()