from app.application.dto.execution_dto import ExecutionResultResponse, SubmitOrderRequest
from app.domain.entities.execution import ExecutionOrderRequest
from app.domain.repositories.execution_repository import ExecutionAuditRepository
from app.infrastructure.execution.execution_gateway import ExecutionGateway


async def submit_execution_order_use_case(
    payload: SubmitOrderRequest, audit_repository: ExecutionAuditRepository
) -> ExecutionResultResponse:
    order = ExecutionOrderRequest(
        symbol=payload.symbol,
        side=payload.side,
        quantity=payload.quantity,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        confirmation_phrase=payload.confirmation_phrase,
    )
    gateway = ExecutionGateway()
    result = await gateway.submit_order(order, open_positions_count=0, daily_loss_pct=0.0)

    await audit_repository.log_attempt(
        level="warning" if result.status == "rejected" else "info",
        message=f"Execution order attempt for {payload.symbol} {payload.side} -> {result.status}",
        context={
            "symbol": payload.symbol,
            "side": payload.side,
            "quantity": payload.quantity,
            "stop_loss": payload.stop_loss,
            "take_profit": payload.take_profit,
            "result_status": result.status,
            "result_reason": result.reason,
        },
    )

    return ExecutionResultResponse(
        status=result.status, reason=result.reason, broker_order_id=result.broker_order_id
    )
