from uuid import UUID

from fastapi import HTTPException, status

from app.domain.repositories.backtest_repository import BacktestRepository


async def deactivate_strategy_use_case(strategy_id: UUID, repository: BacktestRepository) -> None:
    found = await repository.deactivate_strategy(strategy_id)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")


async def delete_strategy_use_case(strategy_id: UUID, repository: BacktestRepository) -> None:
    found = await repository.delete_strategy(strategy_id)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
