from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.backtest_dto import (
    BacktestIntervalResult,
    BacktestRunRequest,
    BacktestRunResponse,
    BacktestStatisticsSchema,
    TradeResultSchema,
)
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.entities.backtest import Metric, Signal, Trade
from app.domain.entities.market import Candle
from app.domain.repositories.backtest_repository import BacktestRepository
from app.domain.repositories.market_repository import MarketRepository
from app.domain.services.backtest_engine import (
    BacktestConfig,
    Condition,
    RuleGroup,
    compute_statistics,
    run_backtest,
)
from app.domain.services.feature_engine import compute_feature_rows
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient


def _to_rule_group(schema) -> RuleGroup | None:
    if schema is None:
        return None
    return RuleGroup(
        match=schema.match,
        conditions=[
            Condition(field=condition.field, operator=condition.operator, value=condition.value)
            for condition in schema.conditions
        ],
    )


async def run_backtest_use_case(
    payload: BacktestRunRequest,
    market_repository: MarketRepository,
    backtest_repository: BacktestRepository,
    client: TwelveDataClient,
) -> BacktestRunResponse:
    strategy_entity = await backtest_repository.get_or_create_strategy(
        name=payload.strategy_name,
        description=payload.strategy_description,
        parameters=payload.model_dump(exclude={"intervals", "limit"}),
    )

    config_base = BacktestConfig(
        symbol=payload.symbol,
        entry_long_rules=_to_rule_group(payload.entry_long_rules),
        entry_short_rules=_to_rule_group(payload.entry_short_rules),
        initial_balance=payload.initial_balance,
        risk_per_trade_pct=payload.risk_per_trade_pct,
        spread_pips=payload.spread_pips,
        slippage_pips=payload.slippage_pips,
        commission_per_trade=payload.commission_per_trade,
        stop_loss_atr_multiple=payload.stop_loss_atr_multiple,
        take_profit_atr_multiple=payload.take_profit_atr_multiple,
        max_holding_bars=payload.max_holding_bars,
    )

    interval_results: list[BacktestIntervalResult] = []

    for interval in payload.intervals:
        candle_responses = await get_historical_candles(
            payload.symbol, interval, payload.limit, market_repository, client
        )
        candles = [
            Candle(
                symbol=payload.symbol,
                interval=interval,
                open=item.open,
                high=item.high,
                low=item.low,
                close=item.close,
                volume=item.volume,
                timestamp=item.timestamp,
            )
            for item in candle_responses
        ]
        feature_rows = compute_feature_rows(candles)

        simulated_trades = run_backtest(feature_rows, config_base)
        stats = compute_statistics(simulated_trades, payload.initial_balance)

        trade_schemas: list[TradeResultSchema] = []
        for simulated in simulated_trades:
            signal = Signal(
                id=uuid4(),
                strategy_id=strategy_entity.id,
                symbol=payload.symbol,
                direction=simulated.side,
                confidence=1.0,
                reasoning={
                    "strategy": payload.strategy_name,
                    "interval": interval,
                    "entry_snapshot": simulated.entry_snapshot,
                    "stop_loss_atr_multiple": payload.stop_loss_atr_multiple,
                    "take_profit_atr_multiple": payload.take_profit_atr_multiple,
                },
                created_at=simulated.opened_at,
            )
            saved_signal = await backtest_repository.save_signal(signal)

            r_multiple = simulated.pnl / simulated.risk_amount if simulated.risk_amount else None
            trade = Trade(
                id=uuid4(),
                signal_id=saved_signal.id,
                symbol=payload.symbol,
                side=simulated.side,
                entry_price=simulated.entry_price,
                exit_price=simulated.exit_price,
                quantity=simulated.quantity,
                status="closed",
                is_paper=True,
                pnl=simulated.pnl,
                opened_at=simulated.opened_at,
                closed_at=simulated.closed_at,
            )
            await backtest_repository.save_trade(trade)

            trade_schemas.append(
                TradeResultSchema(
                    side=simulated.side,
                    entry_price=simulated.entry_price,
                    exit_price=simulated.exit_price,
                    quantity=simulated.quantity,
                    pnl=simulated.pnl,
                    r_multiple=r_multiple,
                    opened_at=simulated.opened_at,
                    closed_at=simulated.closed_at,
                    exit_reason=simulated.exit_reason,
                )
            )

        recorded_timestamp = (
            simulated_trades[-1].closed_at if simulated_trades else datetime.now(UTC)
        )
        metric_tags = {
            "strategy": payload.strategy_name,
            "symbol": payload.symbol,
            "interval": interval,
        }
        metrics = [
            Metric(
                id=uuid4(), name=name, value=value, tags=metric_tags, recorded_at=recorded_timestamp
            )
            for name, value in [
                ("win_rate", stats["win_rate"]),
                ("profit_factor", stats["profit_factor"]),
                ("sharpe_ratio", stats["sharpe_ratio"]),
                ("sortino_ratio", stats["sortino_ratio"]),
                ("max_drawdown_pct", stats["max_drawdown_pct"]),
                ("average_r_multiple", stats["average_r_multiple"]),
                ("final_equity", stats["final_equity"]),
            ]
            if value is not None
        ]
        await backtest_repository.save_metrics(metrics)

        interval_results.append(
            BacktestIntervalResult(
                interval=interval,
                trades=trade_schemas,
                statistics=BacktestStatisticsSchema(**stats),
            )
        )

    return BacktestRunResponse(
        strategy_id=str(strategy_entity.id),
        strategy_name=strategy_entity.name,
        symbol=payload.symbol,
        results=interval_results,
    )
