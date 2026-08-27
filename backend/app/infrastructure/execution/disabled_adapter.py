from app.domain.entities.execution import ExecutionOrderRequest, ExecutionResult
from app.infrastructure.execution.broker_adapter import BrokerAdapter


class NoBrokerConfiguredAdapter(BrokerAdapter):
    async def place_order(self, order: ExecutionOrderRequest) -> ExecutionResult:
        return ExecutionResult(
            status="rejected",
            reason=(
                "No broker adapter is implemented yet. The execution engine "
                "architecture is ready for a future broker integration, but no "
                "live broker connection exists in this codebase."
            ),
            broker_order_id=None,
        )
