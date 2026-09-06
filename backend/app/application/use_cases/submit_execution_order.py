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

    open_positions_count = 0
    daily_loss_pct = 0.0
    portfolio_note = (
    "No portfolio specified; risk checks used conservative defaults "
    "(0 open positions, 0% daily loss)."
)

    if payload.portfolio_id is not None:
        portfolio = await paper_trading_repository.get_portfolio(
            UUID(payload.portfolio_id), user_id
        )
        if portfolio is not None:
            open_positions_count = await paper_trading_repository.get_open_trade_count(portfolio.id)
            daily_loss_pct = await paper_trading_repository.get_daily_pnl_pct(portfolio.id)
            portfolio_note = f"Risk checks used real data from portfolio {portfolio.name}."
        else:
            portfolio_note = (
    "Specified portfolio was not found or not owned by this user; "
    "used conservative defaults."
)

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
            "portfolio_note": portfolio_note,
        },
    )

    return ExecutionResultResponse(
        status=result.status, reason=result.reason, broker_order_id=result.broker_order_id
    )
