from abc import ABC, abstractmethod

from app.domain.entities.execution import ExecutionOrderRequest, ExecutionResult


class BrokerAdapter(ABC):
    @abstractmethod
    async def place_order(self, order: ExecutionOrderRequest) -> ExecutionResult:
        raise NotImplementedError
