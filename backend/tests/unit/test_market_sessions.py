from datetime import UTC, datetime

from app.core.market_sessions import get_active_sessions


def test_london_session_active_at_10_utc():
    moment = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
    assert "London" in get_active_sessions(moment)


def test_sydney_session_active_late_evening_utc():
    moment = datetime(2026, 1, 5, 23, 0, tzinfo=UTC)
    assert "Sydney" in get_active_sessions(moment)


def test_london_and_new_york_overlap_at_15_utc():
    moment = datetime(2026, 1, 5, 15, 0, tzinfo=UTC)
    sessions = get_active_sessions(moment)
    assert "London" in sessions
    assert "New York" in sessions
