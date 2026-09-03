from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.ai_dto import ModelTrainingResult, TrainModelsRequest, TrainModelsResponse
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.entities.market import Candle
from app.domain.repositories.market_repository import MarketRepository
from app.domain.services.ai_training import (
    train_confidence_model,
    train_opportunity_model,
    train_regime_model,
    train_reward_model,
    train_risk_model,
    train_trend_classifier,
)
from app.domain.services.dataset_builder import build_training_dataset, label_market_regimes
from app.domain.services.feature_engine import compute_feature_rows
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.ml.model_registry import save_model


def _model_key(symbol: str, interval: str) -> str:
    return f"{symbol.replace('/', '_')}_{interval}"


async def train_models_use_case(
    payload: TrainModelsRequest,
    repository: MarketRepository,
    client: TwelveDataClient,
    session: AsyncSession,
) -> TrainModelsResponse:
    candle_responses = await get_historical_candles(
        payload.symbol, payload.interval, payload.limit, repository, client
    )
    candles = [
        Candle(
            symbol=payload.symbol,
            interval=payload.interval,
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
    dataset = build_training_dataset(feature_rows, horizon=payload.horizon)

    if len(dataset) < payload.minimum_samples:
        raise ValueError(
            f"Not enough training samples ({len(dataset)}) for {payload.symbol} {payload.interval}; "
            f"need at least {payload.minimum_samples}. Increase limit or lower minimum_samples."
        )

    regime_labels = label_market_regimes(dataset)
    key = _model_key(payload.symbol, payload.interval)
    results: list[ModelTrainingResult] = []

    trend_model, trend_metrics = train_trend_classifier(dataset)
    version = await save_model(session, f"trend_classifier_{key}", trend_model, trend_metrics)
    results.append(ModelTrainingResult(model_name="trend_classifier", version=version, metrics=trend_metrics))

    opportunity_model, opportunity_metrics = train_opportunity_model(dataset)
    version = await save_model(session, f"entry_quality_{key}", opportunity_model, opportunity_metrics)
    results.append(ModelTrainingResult(model_name="entry_quality", version=version, metrics=opportunity_metrics))

    confidence_model, confidence_metrics = train_confidence_model(dataset)
    version = await save_model(session, f"confidence_scoring_{key}", confidence_model, confidence_metrics)
    results.append(
        ModelTrainingResult(model_name="confidence_scoring", version=version, metrics=confidence_metrics)
    )

    risk_model, risk_metrics = train_risk_model(dataset)
    version = await save_model(session, f"risk_prediction_{key}", risk_model, risk_metrics)
    results.append(ModelTrainingResult(model_name="risk_prediction", version=version, metrics=risk_metrics))

    reward_model, reward_metrics = train_reward_model(dataset)
    version = await save_model(session, f"reward_prediction_{key}", reward_model, reward_metrics)
    results.append(ModelTrainingResult(model_name="reward_prediction", version=version, metrics=reward_metrics))

    regime_model, regime_metrics = train_regime_model(dataset, regime_labels)
    version = await save_model(session, f"market_regime_{key}", regime_model, regime_metrics)
    results.append(ModelTrainingResult(model_name="market_regime", version=version, metrics=regime_metrics))

    return TrainModelsResponse(
        symbol=payload.symbol,
        interval=payload.interval,
        dataset_size=len(dataset),
        models=results,
    )