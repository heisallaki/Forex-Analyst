from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.ai_dto import ModelStatusEntry, ModelStatusResponse
from app.infrastructure.ml.model_registry import get_model_metadata, has_model

MODEL_KEYS = [
    "trend_classifier",
    "entry_quality",
    "confidence_scoring",
    "risk_prediction",
    "reward_prediction",
    "market_regime",
]


async def get_model_status_use_case(
    symbol: str, interval: str, session: AsyncSession
) -> ModelStatusResponse:
    key = symbol.replace("/", "_") + f"_{interval}"
    entries: list[ModelStatusEntry] = []
    for model_key in MODEL_KEYS:
        full_name = f"{model_key}_{key}"
        trained = await has_model(session, full_name)
        metadata = await get_model_metadata(session, full_name) if trained else None
        entries.append(
            ModelStatusEntry(
                model_name=model_key,
                trained=trained,
                trained_at=metadata.get("trained_at") if metadata else None,
                metrics=metadata,
            )
        )
    return ModelStatusResponse(
        symbol=symbol,
        interval=interval,
        models=entries,
        all_trained=all(entry.trained for entry in entries),
    )
