import asyncio
import logging

from app.application.use_cases.evaluate_signals import evaluate_pending_signals_use_case
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.backtest_repository_impl import SqlAlchemyBacktestRepository
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

logger = logging.getLogger(__name__)

EVALUATION_INTERVAL_SECONDS = 3600


async def run_signal_accuracy_evaluator() -> None:
    while True:
        try:
            async with AsyncSessionLocal() as session:
                backtest_repository = SqlAlchemyBacktestRepository(session)
                market_repository = SqlAlchemyMarketRepository(session)
                client = TwelveDataClient()
                result = await evaluate_pending_signals_use_case(
                    backtest_repository, market_repository, client
                )
                if result.evaluated > 0:
                    logger.info(
                        "Signal accuracy evaluator: evaluated %s signal(s), "
                        "%s skipped (not enough data yet)",
                        result.evaluated,
                        result.skipped,
                    )
        except asyncio.CancelledError:
            raise
        except Exception as error:
            logger.warning("Signal accuracy evaluator failed this cycle: %s", error)

        await asyncio.sleep(EVALUATION_INTERVAL_SECONDS)
