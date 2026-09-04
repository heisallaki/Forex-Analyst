from datetime import datetime, timedelta, timezone

from app.domain.services.backtest_engine import BacktestConfig, Condition, RuleGroup, run_backtest


def _row(minute_offset, open_, high, low, close, atr=0.001, rsi=50):
    return {
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minute_offset),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "atr_14": atr,
        "rsi_14": rsi,
    }


def test_run_backtest_opens_and_closes_a_long_trade_on_take_profit():
    rows = [
        _row(0, 1.1000, 1.1005, 1.0995, 1.1000, rsi=20),
        _row(1, 1.1000, 1.1005, 1.0995, 1.1000),
        _row(2, 1.1050, 1.1200, 1.1040, 1.1050),
    ]
    config = BacktestConfig(
        symbol="EUR/USD",
        entry_long_rules=RuleGroup(match="all", conditions=[Condition(field="rsi_14", operator="lt", value=30)]),
        entry_short_rules=None,
        initial_balance=10000,
        risk_per_trade_pct=1,
        spread_pips=0,
        slippage_pips=0,
        commission_per_trade=0,
        stop_loss_atr_multiple=1.0,
        take_profit_atr_multiple=2.0,
        max_holding_bars=10,
    )
    trades = run_backtest(rows, config)
    assert len(trades) == 1
    assert trades[0].side == "long"
    assert trades[0].exit_reason == "take_profit"
    assert trades[0].pnl > 0


def test_run_backtest_closes_on_stop_loss():
    rows = [
        _row(0, 1.1000, 1.1005, 1.0995, 1.1000, rsi=20),
        _row(1, 1.1000, 1.1005, 1.0995, 1.1000),
        _row(2, 1.0950, 1.0955, 1.0940, 1.0945),
    ]
    config = BacktestConfig(
        symbol="EUR/USD",
        entry_long_rules=RuleGroup(match="all", conditions=[Condition(field="rsi_14", operator="lt", value=30)]),
        entry_short_rules=None,
        initial_balance=10000,
        risk_per_trade_pct=1,
        spread_pips=0,
        slippage_pips=0,
        commission_per_trade=0,
        stop_loss_atr_multiple=1.0,
        take_profit_atr_multiple=2.0,
        max_holding_bars=10,
    )
    trades = run_backtest(rows, config)
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_loss"
    assert trades[0].pnl < 0