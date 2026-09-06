from uuid import UUID

from app.application.dto.execution_dto import ExecutionResultResponse, SubmitOrderRequest
from app.domain.entities.execution import ExecutionOrderRequest
from app.domain.repositories.execution_repository import ExecutionAuditRepository
from app.domain.repositories.paper_trading_repository import PaperTradingRepository
from app.infrastructure.execution.execution_gateway import ExecutionGateway


async def submit_execution_order_use_case(
    payload: SubmitOrderRequest,
    audit_repository: ExecutionAuditRepository,
    paper_trading_repository: PaperTradingRepository,
    user_id: UUID,
) -> ExecutionResultResponse:
    order = ExecutionOrderRequest(
        symbol=payload.symbol,
        side=payload.side,
        quantity=payload.quantity,
        stop_loss=payload.stop_loss,
        take_profit=payload.take_profit,
        confirmation_phrase=payload.confirmation_phrase,
    )

    open_positions_count = await paper_trading_repository.get_account_open_trade_count(user_id)
    daily_loss_pct = await paper_trading_repository.get_account_daily_pnl_pct(user_id)

    gateway = ExecutionGateway()
    result = await gateway.submit_order(
        order, open_positions_count=open_positions_count, daily_loss_pct=daily_loss_pct
    )

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
            "open_positions_count": open_positions_count,
            "daily_loss_pct": daily_loss_pct,
            "portfolio_id_hint": payload.portfolio_id,
            "note": "Risk checks aggregated across all portfolios owned by this user.",
        },
    )

    return ExecutionResultResponse(
        status=result.status, reason=result.reason, broker_order_id=result.broker_order_id
    )
