from app.core.config import settings
from app.domain.entities.execution import ExecutionOrderRequest, ExecutionResult
from app.domain.services.risk_management import REQUIRED_CONFIRMATION_PHRASE, validate_risk
from app.infrastructure.execution.disabled_adapter import NoBrokerConfiguredAdapter


class ExecutionGateway:
    def __init__(self) -> None:
        self._adapter = NoBrokerConfiguredAdapter()

    async def submit_order(
        self, order: ExecutionOrderRequest, open_positions_count: int, daily_loss_pct: float
    ) -> ExecutionResult:
        if not settings.EXECUTION_ENABLED:
            return ExecutionResult(
                status="rejected",
                reason=(
                    "Live execution is disabled by configuration "
                    "(EXECUTION_ENABLED=false). This is the default and intentional. "
                    "No live trading occurs."
                ),
                broker_order_id=None,
            )

        if order.confirmation_phrase != REQUIRED_CONFIRMATION_PHRASE:
            return ExecutionResult(
                status="rejected",
                reason=(
                    "Confirmation phrase did not match the required exact text. "
                    "No order was submitted."
                ),
                broker_order_id=None,
            )

        violations = validate_risk(
            quantity=order.quantity,
            stop_loss=order.stop_loss,
            max_position_size=settings.EXECUTION_MAX_POSITION_SIZE,
            open_positions_count=open_positions_count,
            max_open_positions=settings.EXECUTION_MAX_OPEN_POSITIONS,
            daily_loss_pct=daily_loss_pct,
            max_daily_loss_pct=settings.EXECUTION_MAX_DAILY_LOSS_PCT,
        )
        if violations:
            return ExecutionResult(
                status="rejected", reason="; ".join(violations), broker_order_id=None
            )

        return await self._adapter.place_order(order)
