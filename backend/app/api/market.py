import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user_from_token,
    get_db_session,
    require_admin,
    require_permission,
)
from app.application.dto.market_dto import (
    BackfillRequest,
    BackfillResponse,
    CandleResponse,
    MarketStatusResponse,
)
from app.application.use_cases.backfill_candles import backfill_candles
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.core.config import settings
from app.core.market_sessions import get_active_sessions
from app.domain.entities.user import User
from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.market_data.twelve_data_stream import MARKET_TICKS_CHANNEL
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/status", response_model=MarketStatusResponse)
async def market_status(
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
) -> MarketStatusResponse:
    return MarketStatusResponse(
        instruments=settings.MARKET_INSTRUMENTS,
        active_sessions=get_active_sessions(),
    )


@router.get("/candles/{symbol:path}", response_model=list[CandleResponse])
async def candles(
    symbol: str,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    interval: str = Query(default="1min"),
    limit: int = Query(default=100, ge=1, le=5000),
) -> list[CandleResponse]:
    repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    return await get_historical_candles(symbol, interval, limit, repository, client)


@router.post("/backfill", response_model=BackfillResponse)
async def backfill(
    payload: BackfillRequest,
    current_user: Annotated[User, Depends(require_admin())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> BackfillResponse:
    repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    return await backfill_candles(payload, repository, client)


@router.websocket("/ws/prices")
async def prices_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return

    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)
        user = await get_current_user_from_token(token, repository)

    if user is None or not user.permissions.get("view_markets", False):
        await websocket.close(code=4403)
        return

    await websocket.accept()
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(MARKET_TICKS_CHANNEL)

    async def sender() -> None:
        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is not None:
                    await websocket.send_text(message["data"])
                await asyncio.sleep(0.01)
            except (WebSocketDisconnect, asyncio.CancelledError):
                raise
            except Exception as error:
                logger.warning("Market WebSocket sender hiccup for user %s: %s", user.id, error)
                await asyncio.sleep(1.0)

    async def receiver() -> None:
        while True:
            await websocket.receive_text()

    sender_task = asyncio.create_task(sender())
    receiver_task = asyncio.create_task(receiver())

    try:
        done, pending = await asyncio.wait(
            {sender_task, receiver_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            error = task.exception() if not task.cancelled() else None
            if error is not None and not isinstance(error, WebSocketDisconnect):
                logger.warning("Market WebSocket connection ending for user %s: %s", user.id, error)
        for task in pending:
            task.cancel()
    except WebSocketDisconnect:
        pass
    finally:
        sender_task.cancel()
        receiver_task.cancel()
        await pubsub.unsubscribe(MARKET_TICKS_CHANNEL)
        await pubsub.close()
        try:
            await websocket.close()
        except RuntimeError:
            pass
