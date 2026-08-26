import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Condition:
    field: str
    operator: str
    value: float


@dataclass
class RuleGroup:
    conditions: list[Condition]
    match: str = "all"


@dataclass
class BacktestConfig:
    symbol: str
    entry_long_rules: RuleGroup | None
    entry_short_rules: RuleGroup | None
    initial_balance: float
    risk_per_trade_pct: float
    spread_pips: float
    slippage_pips: float
    commission_per_trade: float
    stop_loss_atr_multiple: float
    take_profit_atr_multiple: float
    max_holding_bars: int


@dataclass
class SimulatedTrade:
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    risk_amount: float
    opened_at: datetime
    closed_at: datetime
    exit_reason: str
    entry_snapshot: dict


def _pip_size(symbol: str) -> float:
    upper_symbol = symbol.upper()
    if "JPY" in upper_symbol:
        return 0.01
    if "XAU" in upper_symbol:
        return 0.01
    return 0.0001


def evaluate_condition(row: dict, condition: Condition) -> bool:
    value = row.get(condition.field)
    if value is None:
        return False
    if condition.operator == "lt":
        return value < condition.value
    if condition.operator == "lte":
        return value <= condition.value
    if condition.operator == "gt":
        return value > condition.value
    if condition.operator == "gte":
        return value >= condition.value
    if condition.operator == "eq":
        return value == condition.value
    raise ValueError(f"Unsupported operator: {condition.operator}")


def evaluate_rule_group(row: dict, group: RuleGroup | None) -> bool:
    if group is None or not group.conditions:
        return False
    results = [evaluate_condition(row, condition) for condition in group.conditions]
    return all(results) if group.match == "all" else any(results)


def run_backtest(feature_rows: list[dict], config: BacktestConfig) -> list[SimulatedTrade]:
    pip_size = _pip_size(config.symbol)
    spread = config.spread_pips * pip_size
    slippage = config.slippage_pips * pip_size

    equity = config.initial_balance
    trades: list[SimulatedTrade] = []
    position: dict | None = None

    for i in range(1, len(feature_rows)):
        row = feature_rows[i]
        signal_row = feature_rows[i - 1]

        if position is not None:
            bars_held = i - position["entry_index"]
            exit_price = None
            exit_reason = None

            if position["side"] == "long":
                if row["low"] <= position["stop_loss"]:
                    exit_price = position["stop_loss"]
                    exit_reason = "stop_loss"
                elif row["high"] >= position["take_profit"]:
                    exit_price = position["take_profit"]
                    exit_reason = "take_profit"
            else:
                if row["high"] >= position["stop_loss"]:
                    exit_price = position["stop_loss"]
                    exit_reason = "stop_loss"
                elif row["low"] <= position["take_profit"]:
                    exit_price = position["take_profit"]
                    exit_reason = "take_profit"

            if exit_price is None and bars_held >= config.max_holding_bars:
                exit_price = row["close"]
                exit_reason = "time_stop"

            if exit_price is not None:
                direction_multiplier = 1 if position["side"] == "long" else -1
                pnl = (
                    (exit_price - position["entry_price"])
                    * direction_multiplier
                    * position["quantity"]
                )
                pnl -= config.commission_per_trade
                equity += pnl
                trades.append(
                    SimulatedTrade(
                        side=position["side"],
                        entry_price=position["entry_price"],
                        exit_price=exit_price,
                        quantity=position["quantity"],
                        pnl=pnl,
                        risk_amount=position["risk_amount"],
                        opened_at=position["opened_at"],
                        closed_at=row["timestamp"],
                        exit_reason=exit_reason,
                        entry_snapshot=position["entry_snapshot"],
                    )
                )
                position = None
            continue

        atr = signal_row.get("atr_14")
        if atr is None or atr <= 0:
            continue

        entered_long = evaluate_rule_group(signal_row, config.entry_long_rules)
        entered_short = evaluate_rule_group(signal_row, config.entry_short_rules)

        if entered_long or entered_short:
            side = "long" if entered_long else "short"
            raw_entry = row["open"]
            entry_price = (
                raw_entry + spread / 2 + slippage
                if side == "long"
                else raw_entry - spread / 2 - slippage
            )
            sl_distance = atr * config.stop_loss_atr_multiple
            tp_distance = atr * config.take_profit_atr_multiple

            if side == "long":
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + tp_distance
            else:
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - tp_distance

            risk_amount = equity * (config.risk_per_trade_pct / 100)
            quantity = risk_amount / sl_distance if sl_distance > 0 else 0.0

            if quantity <= 0:
                continue

            position = {
                "side": side,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "quantity": quantity,
                "risk_amount": risk_amount,
                "opened_at": row["timestamp"],
                "entry_index": i,
                "entry_snapshot": {
                    "matched_rules": "entry_long" if side == "long" else "entry_short",
                    "rsi_14": signal_row.get("rsi_14"),
                    "macd": signal_row.get("macd"),
                    "adx_14": signal_row.get("adx_14"),
                    "market_structure": signal_row.get("market_structure"),
                    "atr_14": atr,
                },
            }

    return trades


def compute_statistics(trades: list[SimulatedTrade], initial_balance: float) -> dict:
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": None,
            "profit_factor": None,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "average_r_multiple": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown_pct": 0.0,
            "final_equity": initial_balance,
            "monthly_performance": {},
        }

    wins = [trade for trade in trades if trade.pnl > 0]
    losses = [trade for trade in trades if trade.pnl <= 0]
    gross_profit = sum(trade.pnl for trade in wins)
    gross_loss = sum(trade.pnl for trade in losses)
    win_rate = len(wins) / len(trades) * 100
    profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else None

    equity = initial_balance
    equity_curve = [initial_balance]
    returns: list[float] = []
    r_multiples: list[float] = []

    for trade in trades:
        returns.append(trade.pnl / equity if equity != 0 else 0.0)
        if trade.risk_amount:
            r_multiples.append(trade.pnl / trade.risk_amount)
        equity += trade.pnl
        equity_curve.append(equity)

    mean_return = statistics.mean(returns)
    std_return = statistics.pstdev(returns) if len(returns) > 1 else 0.0
    downside_returns = [value for value in returns if value < 0]
    downside_std = statistics.pstdev(downside_returns) if len(downside_returns) > 1 else 0.0

    span_days = max((trades[-1].closed_at - trades[0].opened_at).total_seconds() / 86400, 1.0)
    trades_per_year = (len(trades) / span_days) * 365.25

    sharpe_ratio = (mean_return / std_return) * (trades_per_year**0.5) if std_return > 0 else None
    sortino_ratio = (
        (mean_return / downside_std) * (trades_per_year**0.5) if downside_std > 0 else None
    )

    peak = equity_curve[0]
    max_drawdown_pct = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        drawdown = (peak - value) / peak * 100 if peak > 0 else 0.0
        max_drawdown_pct = max(max_drawdown_pct, drawdown)

    average_r_multiple = statistics.mean(r_multiples) if r_multiples else None

    monthly: dict[str, float] = defaultdict(float)
    for trade in trades:
        key = trade.closed_at.strftime("%Y-%m")
        monthly[key] += trade.pnl

    return {
        "total_trades": len(trades),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "average_r_multiple": average_r_multiple,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "max_drawdown_pct": max_drawdown_pct,
        "final_equity": equity,
        "monthly_performance": dict(monthly),
    }
