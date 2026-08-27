from abc import ABC, abstractmethod


class ExecutionAuditRepository(ABC):
    @abstractmethod
    async def log_attempt(self, level: str, message: str, context: dict) -> None:
        raise NotImplementedError
