from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.execution_repository import ExecutionAuditRepository
from app.infrastructure.database.models.log_model import LogModel


class SqlAlchemyExecutionAuditRepository(ExecutionAuditRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_attempt(self, level: str, message: str, context: dict) -> None:
        model = LogModel(level=level, source="execution_engine", message=message, context=context)
        self.session.add(model)
        await self.session.commit()
