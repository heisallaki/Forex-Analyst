import io
from datetime import UTC, datetime

import joblib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.trained_model_model import TrainedModelModel


async def save_model(session: AsyncSession, model_name: str, model, metadata: dict) -> str:
    version = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")

    buffer = io.BytesIO()
    joblib.dump(model, buffer)

    metadata_with_version = dict(metadata)
    metadata_with_version["version"] = version
    metadata_with_version["trained_at"] = datetime.now(UTC).isoformat()

    db_model = TrainedModelModel(
        model_name=model_name,
        version=version,
        model_blob=buffer.getvalue(),
        model_metadata=metadata_with_version,
    )
    session.add(db_model)
    await session.commit()
    return version


async def load_latest_model(session: AsyncSession, model_name: str):
    result = await session.execute(
        select(TrainedModelModel)
        .where(TrainedModelModel.model_name == model_name)
        .order_by(TrainedModelModel.created_at.desc())
        .limit(1)
    )
    db_model = result.scalar_one_or_none()
    if db_model is None:
        return None, None

    model = joblib.load(io.BytesIO(db_model.model_blob))
    return model, db_model.model_metadata


async def has_model(session: AsyncSession, model_name: str) -> bool:
    result = await session.execute(
        select(TrainedModelModel.id).where(TrainedModelModel.model_name == model_name).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def get_model_metadata(session: AsyncSession, model_name: str) -> dict | None:
    _, metadata = await load_latest_model(session, model_name)
    return metadata
