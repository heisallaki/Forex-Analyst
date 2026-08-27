from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.paper_trading_dto import CreatePortfolioRequest, PortfolioResponse
from app.domain.entities.paper_trading import Portfolio
from app.domain.repositories.paper_trading_repository import PaperTradingRepository


async def create_portfolio_use_case(
    payload: CreatePortfolioRequest, user_id: UUID, repository: PaperTradingRepository
) -> PortfolioResponse:
    portfolio = Portfolio(
        id=uuid4(),
        user_id=user_id,
        name=payload.name,
        base_currency=payload.base_currency,
        initial_balance=payload.initial_balance,
        current_balance=payload.initial_balance,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    created = await repository.create_portfolio(portfolio)
    return PortfolioResponse(
        id=str(created.id),
        name=created.name,
        base_currency=created.base_currency,
        initial_balance=created.initial_balance,
        current_balance=created.current_balance,
        created_at=created.created_at,
    )
