from uuid import uuid4

import pandas as pd

from app.application.dto.ai_dto import ModelPrediction, PredictMarketResponse
from app.application.use_cases.get_historical_candles import get_historical_candles
from app.domain.entities.ai import AIPrediction
from app.domain.entities.market import Candle
from app.domain.repositories.ai_prediction_repository import AIPredictionRepository
from app.domain.repositories.market_repository import MarketRepository
from app.domain.services.dataset_builder import (
    ML_FEATURE_COLUMNS,
    REGIME_FEATURE_COLUMNS,
    row_to_ml_features,
)
from app.domain.services.feature_engine import compute_feature_rows
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient
from app.infrastructure.ml.model_registry import load_latest_model

TREND_LABEL_MAP = {0: "down", 1: "flat", 2: "up"}


async def _save_and_wrap(
    repository: AIPredictionRepository,
    model_name: str,
    symbol: str,
    prediction_type: str,
    output: dict,
) -> ModelPrediction:
    prediction = AIPrediction(
        id=uuid4(),
        model_name=model_name,
        symbol=symbol,
        prediction_type=prediction_type,
        output=output,
        created_at=None,
    )
    saved = await repository.save_prediction(prediction)
    return ModelPrediction(
        model_name=model_name,
        prediction_type=prediction_type,
        output=output,
        created_at=saved.created_at,
    )


async def predict_market_with_features(
    symbol: str,
    interval: str,
    market_repository: MarketRepository,
    prediction_repository: AIPredictionRepository,
    client: TwelveDataClient,
) -> tuple[PredictMarketResponse, dict]:
    candle_responses = await get_historical_candles(
        symbol, interval, 100, market_repository, client
    )
    candles = [
        Candle(
            symbol=symbol,
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
    if not feature_rows:
        raise ValueError(f"No feature data available for {symbol} {interval}")

    latest_row = feature_rows[-1]
    ml_features = row_to_ml_features(latest_row)
    if ml_features is None or any(value is None for value in ml_features.values()):
        raise ValueError(
            "Insufficient indicator warm-up data to generate a prediction for the latest bar"
        )

    feature_frame = pd.DataFrame([ml_features])
    key = symbol.replace("/", "_") + f"_{interval}"
    predictions: list[ModelPrediction] = []

    trend_model, _ = load_latest_model(f"trend_classifier_{key}")
    trend_output = {"error": "model not trained yet"}
    if trend_model is not None:
        probabilities = trend_model.predict_proba(feature_frame[ML_FEATURE_COLUMNS])[0]
        predicted_class = int(probabilities.argmax())
        trend_output = {
            "predicted_trend": TREND_LABEL_MAP[predicted_class],
            "probabilities": {
                TREND_LABEL_MAP[i]: float(probabilities[i]) for i in range(len(probabilities))
            },
        }
    predictions.append(
        await _save_and_wrap(
            prediction_repository, "trend_classifier", symbol, "trend", trend_output
        )
    )

    opportunity_model, _ = load_latest_model(f"entry_quality_{key}")
    opportunity_output = {"error": "model not trained yet"}
    if opportunity_model is not None:
        probability = float(
            opportunity_model.predict_proba(feature_frame[ML_FEATURE_COLUMNS])[0][1]
        )
        opportunity_output = {"opportunity_probability": probability}
    predictions.append(
        await _save_and_wrap(
            prediction_repository, "entry_quality", symbol, "entry_quality", opportunity_output
        )
    )

    confidence_model, _ = load_latest_model(f"confidence_scoring_{key}")
    confidence_output = {"error": "model not trained yet"}
    if confidence_model is not None:
        probability = float(confidence_model.predict_proba(feature_frame[ML_FEATURE_COLUMNS])[0][1])
        confidence_output = {"target_before_stop_probability": probability}
    predictions.append(
        await _save_and_wrap(
            prediction_repository, "confidence_scoring", symbol, "confidence", confidence_output
        )
    )

    risk_model, _ = load_latest_model(f"risk_prediction_{key}")
    risk_output = {"error": "model not trained yet"}
    if risk_model is not None:
        predicted_mae = float(risk_model.predict(feature_frame[ML_FEATURE_COLUMNS])[0])
        risk_output = {"predicted_max_adverse_excursion_atr": predicted_mae}
    predictions.append(
        await _save_and_wrap(prediction_repository, "risk_prediction", symbol, "risk", risk_output)
    )

    reward_model, _ = load_latest_model(f"reward_prediction_{key}")
    reward_output = {"error": "model not trained yet"}
    if reward_model is not None:
        predicted_mfe = float(reward_model.predict(feature_frame[ML_FEATURE_COLUMNS])[0])
        reward_output = {"predicted_max_favorable_excursion_atr": predicted_mfe}
    predictions.append(
        await _save_and_wrap(
            prediction_repository, "reward_prediction", symbol, "reward", reward_output
        )
    )

    regime_model, _ = load_latest_model(f"market_regime_{key}")
    regime_output = {"error": "model not trained yet"}
    if regime_model is not None:
        predicted_regime = str(regime_model.predict(feature_frame[REGIME_FEATURE_COLUMNS])[0])
        regime_output = {"predicted_regime": predicted_regime}
    predictions.append(
        await _save_and_wrap(
            prediction_repository, "market_regime", symbol, "regime", regime_output
        )
    )

    response = PredictMarketResponse(
        symbol=symbol,
        interval=interval,
        timestamp=latest_row["timestamp"],
        predictions=predictions,
        note=(
            "These are raw model predictions, not trading recommendations. "
            "The Decision Engine combines these into an explainable recommendation."
        ),
    )
    return response, latest_row


async def predict_market_use_case(
    symbol: str,
    interval: str,
    market_repository: MarketRepository,
    prediction_repository: AIPredictionRepository,
    client: TwelveDataClient,
) -> PredictMarketResponse:
    response, _ = await predict_market_with_features(
        symbol, interval, market_repository, prediction_repository, client
    )
    return response
