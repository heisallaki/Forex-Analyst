import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.admin import router as admin_router
from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.backtest import router as backtest_router
from app.api.decision import router as decision_router
from app.api.execution import router as execution_router
from app.api.features import router as features_router
from app.api.health import router as health_router
from app.api.market import router as market_router
from app.api.paper_trading import router as paper_trading_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.infrastructure.market_data.position_monitor import run_position_monitor
from app.infrastructure.market_data.twelve_data_stream import run_market_stream
from app.infrastructure.scheduler.signal_accuracy_scheduler import run_signal_accuracy_evaluator

configure_logging(settings.APP_DEBUG)
logger = logging.getLogger(__name__)
logger.info("Configured CORS_ORIGINS: %s", settings.CORS_ORIGINS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stream_task = asyncio.create_task(run_market_stream())
    monitor_task = asyncio.create_task(run_position_monitor())
    evaluator_task = asyncio.create_task(run_signal_accuracy_evaluator())
    app.state.stream_task = stream_task
    app.state.monitor_task = monitor_task
    app.state.evaluator_task = evaluator_task
    yield
    stream_task.cancel()
    monitor_task.cancel()
    evaluator_task.cancel()
    for task in (stream_task, monitor_task, evaluator_task):
        try:
            await task
        except asyncio.CancelledError:
            pass


fastapi_app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG, lifespan=lifespan)

fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@fastapi_app.middleware("http")
async def default_rate_limit_state(request: Request, call_next):
    request.state.view_rate_limit = None
    return await call_next(request)


@fastapi_app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True
    )

    detail = str(exc) if settings.APP_DEBUG else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})


fastapi_app.include_router(health_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(auth_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(market_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(features_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(backtest_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(ai_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(decision_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(paper_trading_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(execution_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(users_router, prefix=settings.API_PREFIX)
fastapi_app.include_router(admin_router, prefix=settings.API_PREFIX)

app = CORSMiddleware(
    fastapi_app,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)