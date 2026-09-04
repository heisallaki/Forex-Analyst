from app.domain.services.trading_math import compute_pips, compute_pnl, pip_size


def test_pip_size_for_jpy_pair():
    assert pip_size("USD/JPY") == 0.01


def test_pip_size_for_gold():
    assert pip_size("XAU/USD") == 0.01


def test_pip_size_for_standard_pair():
    assert pip_size("EUR/USD") == 0.0001


def test_compute_pnl_long_profit():
    pnl = compute_pnl("EUR/USD", "long", entry_price=1.1000, exit_price=1.1050, quantity=10000)
    assert round(pnl, 2) == 50.0


def test_compute_pnl_long_loss():
    pnl = compute_pnl("EUR/USD", "long", entry_price=1.1000, exit_price=1.0950, quantity=10000)
    assert round(pnl, 2) == -50.0


def test_compute_pnl_short_profit():
    pnl = compute_pnl("EUR/USD", "short", entry_price=1.1000, exit_price=1.0950, quantity=10000)
    assert round(pnl, 2) == 50.0


def test_compute_pips_long():
    pips = compute_pips("EUR/USD", "long", entry_price=1.1000, exit_price=1.1050)
    assert round(pips, 1) == 50.0
