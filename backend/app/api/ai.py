from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, require_admin, require_permission, require_verified
from app.application.dto.ai_dto import (
    ModelStatusResponse,
    PredictMarketResponse,
    TrainModelsRequest,
    TrainModelsResponse,
)
from app.application.use_cases.get_model_status import get_model_status_use_case
from app.application.use_cases.predict_market import predict_market_use_case
from app.application.use_cases.train_models import train_models_use_case
from app.domain.entities.user import User
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.repositories.ai_prediction_repository_impl import (
    SqlAlchemyAIPredictionRepository,
)
from app.infrastructure.repositories.market_repository_impl import SqlAlchemyMarketRepository

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/train", response_model=TrainModelsResponse)
async def train(
    payload: TrainModelsRequest,
    current_user: Annotated[User, Depends(require_admin())],
    verified_user: Annotated[User, Depends(require_verified())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainModelsResponse:
    repository = SqlAlchemyMarketRepository(session)
    client = TwelveDataClient()
    try:
        return await train_models_use_case(payload, repository, client, session)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/models/status/{symbol:path}", response_model=ModelStatusResponse)
async def model_status(
    symbol: str,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    interval: str = Query(default="1min"),
) -> ModelStatusResponse:
    return await get_model_status_use_case(symbol, interval, session)


@router.get("/predict/{symbol:path}", response_model=PredictMarketResponse)
async def predict(
    symbol: str,
    current_user: Annotated[User, Depends(require_permission("view_markets"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    interval: str = Query(default="1min"),
) -> PredictMarketResponse:
    market_repository = SqlAlchemyMarketRepository(session)
    prediction_repository = SqlAlchemyAIPredictionRepository(session)
    client = TwelveDataClient()
    try:
        return await predict_market_use_case(
            symbol, interval, market_repository, prediction_repository, client
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
