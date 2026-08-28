from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.decision_dto import RecommendationResponse
from app.application.use_cases.predict_market import predict_market_with_features
from app.domain.entities.backtest import Signal
from app.domain.repositories.ai_prediction_repository import AIPredictionRepository
from app.domain.repositories.backtest_repository import BacktestRepository
from app.domain.repositories.market_repository import MarketRepository
from app.domain.services.decision_engine import build_recommendation
from app.infrastructure.market_data.twelve_data_client import TwelveDataClient

DISCLAIMER = (
    "This is an automated analysis and recommendation, not financial advice "
    "and not an executed trade. No position will be opened automatically."
)


async def generate_recommendation_use_case(
    symbol: str,
    interval: str,
    market_repository: MarketRepository,
    prediction_repository: AIPredictionRepository,
    backtest_repository: BacktestRepository,
    client: TwelveDataClient,
    user_id: UUID,
) -> RecommendationResponse:
    prediction_response, latest_row = await predict_market_with_features(
        symbol, interval, market_repository, prediction_repository, client
    )
    predictions_by_type = {
        prediction.model_name: prediction.output for prediction in prediction_response.predictions
    }

    recommendation = build_recommendation(symbol, interval, latest_row, predictions_by_type)

    signal = Signal(
        id=uuid4(),
        strategy_id=None,
        symbol=symbol,
        direction=recommendation["action"],
        confidence=recommendation["confidence"],
        reasoning={
            "trend": recommendation["trend"],
            "risk_level": recommendation["risk_level"],
            "expected_reward_atr": recommendation["expected_reward_atr"],
            "expected_risk_atr": recommendation["expected_risk_atr"],
            "reward_risk_ratio": recommendation["reward_risk_ratio"],
            "market_regime": recommendation["market_regime"],
            "supporting_indicators": recommendation["supporting_indicators"],
            "reasoning": recommendation["reasoning"],
            "alternative_scenarios": recommendation["alternative_scenarios"],
            "invalidation_conditions": recommendation["invalidation_conditions"],
            "source": "decision_engine",
        },
        created_at=datetime.now(UTC),
        user_id=user_id,
    )
    await backtest_repository.save_signal(signal)

    return RecommendationResponse(
        symbol=symbol,
        interval=interval,
        generated_at=datetime.now(UTC),
        action=recommendation["action"],
        trend=recommendation["trend"],
        confidence=recommendation["confidence"],
        risk_level=recommendation["risk_level"],
        expected_reward_atr=recommendation["expected_reward_atr"],
        expected_risk_atr=recommendation["expected_risk_atr"],
        reward_risk_ratio=recommendation["reward_risk_ratio"],
        market_regime=recommendation["market_regime"],
        supporting_indicators=recommendation["supporting_indicators"],
        reasoning=recommendation["reasoning"],
        alternative_scenarios=recommendation["alternative_scenarios"],
        invalidation_conditions=recommendation["invalidation_conditions"],
        disclaimer=DISCLAIMER,
    )
