from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_permission
from app.application.dto.feature_dto import FeatureRow
from app.application.use_cases.compute_features import compute_features
from app.domain.entities.user import User
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/{symbol:path}", response_model=list[FeatureRow])
async def features(
    symbol: str,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    interval: str = Query(default="1min"),
    limit: int = Query(default=200, ge=30, le=5000),
) -> list[FeatureRow]:
    repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    return await compute_features(symbol, interval, limit, repository, client)
