import logging

from app.infrastructure.market_data.position_monitor import _handle_tick


async def test_handle_tick_processes_without_logging_failure(caplog):
    payload = {"symbol": "EUR/USD", "price": "1.1000"}
    with caplog.at_level(logging.WARNING):
        await _handle_tick(payload)
    assert "Position monitor failed to process tick" not in caplog.text
