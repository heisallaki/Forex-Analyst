import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.backtest import router as backtest_router
from app.api.decision import router as decision_router
from app.api.features import router as features_router
from app.api.health import router as health_router
from app.api.market import router as market_router
from app.api.paper_trading import router as paper_trading_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.infrastructure.market_data.position_monitor import run_position_monitor
from app.infrastructure.market_data.twelve_data_stream import run_market_stream

configure_logging(settings.APP_DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stream_task = asyncio.create_task(run_market_stream())
    monitor_task = asyncio.create_task(run_position_monitor())
    yield
    stream_task.cancel()
    monitor_task.cancel()
    for task in (stream_task, monitor_task):
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(market_router, prefix=settings.API_PREFIX)
app.include_router(features_router, prefix=settings.API_PREFIX)
app.include_router(backtest_router, prefix=settings.API_PREFIX)
app.include_router(ai_router, prefix=settings.API_PREFIX)
app.include_router(decision_router, prefix=settings.API_PREFIX)
app.include_router(paper_trading_router, prefix=settings.API_PREFIX)
