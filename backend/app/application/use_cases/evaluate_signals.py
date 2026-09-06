from app.application.dto.backtest_dto import AccuracyStatsResponse, EvaluateSignalsResponse
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.repositories.backtest_repository import BacktestRepository
from app.domain.repositories.market_repository import MarketRepository
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient

TREND_THRESHOLD = 0.0006
LOOKAHEAD_BARS = 20


async def evaluate_pending_signals_use_case(
    backtest_repository: BacktestRepository,
    market_repository: MarketRepository,
    client: TwelveDataClient,
    limit: int = 100,
) -> EvaluateSignalsResponse:
    pending = await backtest_repository.list_signals_for_evaluation(limit)
    evaluated = 0
    skipped = 0

    for signal in pending:
        interval = signal.reasoning.get("interval", "1min")
        candle_responses = await get_historical_candles(
            signal.symbol, interval, 500, market_repository, client
        )
        future_candles = [
            candle for candle in candle_responses if candle.timestamp > signal.created_at
        ]

        if len(future_candles) < LOOKAHEAD_BARS:
            skipped += 1
            continue

        entry_reference = future_candles[0].close
        future_reference = future_candles[LOOKAHEAD_BARS - 1].close
        relative_move = (future_reference - entry_reference) / entry_reference

        if signal.direction == "long":
            outcome = (
                "win"
                if relative_move > TREND_THRESHOLD
                else "loss"
                if relative_move < -TREND_THRESHOLD
                else "flat"
            )
        else:
            outcome = (
                "win"
                if relative_move < -TREND_THRESHOLD
                else "loss"
                if relative_move > TREND_THRESHOLD
                else "flat"
            )

        await backtest_repository.record_signal_outcome(signal.id, outcome)
        evaluated += 1

    return EvaluateSignalsResponse(evaluated=evaluated, skipped=skipped)


async def get_accuracy_stats_use_case(
    backtest_repository: BacktestRepository,
) -> AccuracyStatsResponse:
    stats = await backtest_repository.get_accuracy_stats()
    return AccuracyStatsResponse(**stats)
