from app.domain.services.trading_math import (
    compute_pips,
    compute_pnl,
    is_usd_base_pair,
    pip_size,
    size_quantity_for_risk,
)


def test_pip_size_for_jpy_pair():
    assert pip_size("USD/JPY") == 0.01


def test_pip_size_for_gold():
    assert pip_size("XAU/USD") == 0.01


def test_pip_size_for_standard_pair():
    assert pip_size("EUR/USD") == 0.0001


def test_is_usd_base_pair_detects_usd_as_base():
    assert is_usd_base_pair("USD/JPY") is True
    assert is_usd_base_pair("USD/CHF") is True
    assert is_usd_base_pair("USD/CAD") is True


def test_is_usd_base_pair_false_when_usd_is_quote():
    assert is_usd_base_pair("EUR/USD") is False
    assert is_usd_base_pair("GBP/USD") is False
    assert is_usd_base_pair("XAU/USD") is False


def test_compute_pnl_long_profit_usd_quote_pair():
    pnl = compute_pnl("EUR/USD", "long", entry_price=1.1000, exit_price=1.1050, quantity=10000)
    assert round(pnl, 2) == 50.0


def test_compute_pnl_long_loss_usd_quote_pair():
    pnl = compute_pnl("EUR/USD", "long", entry_price=1.1000, exit_price=1.0950, quantity=10000)
    assert round(pnl, 2) == -50.0


def test_compute_pnl_short_profit_usd_quote_pair():
    pnl = compute_pnl("EUR/USD", "short", entry_price=1.1000, exit_price=1.0950, quantity=10000)
    assert round(pnl, 2) == 50.0


def test_compute_pnl_converts_usd_base_pair_into_usd():
    pnl = compute_pnl("USD/JPY", "long", entry_price=150.00, exit_price=151.00, quantity=1000)
    expected = (151.00 - 150.00) * 1000 / 151.00
    assert round(pnl, 6) == round(expected, 6)


def test_compute_pnl_usd_base_pair_loss_is_negative():
    pnl = compute_pnl("USD/JPY", "long", entry_price=151.00, exit_price=150.00, quantity=1000)
    assert pnl < 0


def test_compute_pips_long():
    pips = compute_pips("EUR/USD", "long", entry_price=1.1000, exit_price=1.1050)
    assert round(pips, 1) == 50.0


def test_size_quantity_for_risk_usd_quote_pair_unchanged():
    quantity = size_quantity_for_risk(
        "EUR/USD", risk_amount_usd=100, stop_distance=0.01, reference_price=1.1
    )
    assert round(quantity, 2) == 10000.0


def test_size_quantity_for_risk_usd_base_pair_scales_by_reference_price():
    quantity = size_quantity_for_risk(
        "USD/JPY", risk_amount_usd=100, stop_distance=1.0, reference_price=150.0
    )
    assert round(quantity, 2) == round(100 * 150.0 / 1.0, 2)


def test_size_quantity_for_risk_zero_stop_distance_returns_zero():
    assert (
        size_quantity_for_risk("EUR/USD", risk_amount_usd=100, stop_distance=0, reference_price=1.1)
        == 0.0
    )
