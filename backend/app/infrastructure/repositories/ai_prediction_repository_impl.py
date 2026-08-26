from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.ai import AIPrediction
from app.domain.repositories.ai_prediction_repository import AIPredictionRepository
from app.infrastructure.database.models.ai_prediction_model import AIPredictionModel


class SqlAlchemyAIPredictionRepository(AIPredictionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_prediction(self, prediction: AIPrediction) -> AIPrediction:
        model = AIPredictionModel(
            id=prediction.id,
            model_name=prediction.model_name,
            symbol=prediction.symbol,
            prediction_type=prediction.prediction_type,
            output=prediction.output,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return AIPrediction(
            id=model.id,
            model_name=model.model_name,
            symbol=model.symbol,
            prediction_type=model.prediction_type,
            output=model.output,
            created_at=model.created_at,
        )
