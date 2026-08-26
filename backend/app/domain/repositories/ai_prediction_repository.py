from abc import ABC, abstractmethod

from app.domain.entities.ai import AIPrediction


class AIPredictionRepository(ABC):
    @abstractmethod
    async def save_prediction(self, prediction: AIPrediction) -> AIPrediction:
        raise NotImplementedError
