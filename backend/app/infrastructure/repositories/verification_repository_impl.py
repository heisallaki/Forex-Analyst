from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.verification import VerificationCode
from app.domain.repositories.verification_repository import VerificationRepository
from app.infrastructure.database.models.verification_code_model import VerificationCodeModel


def _to_entity(model: VerificationCodeModel) -> VerificationCode:
    return VerificationCode(
        id=model.id,
        user_id=model.user_id,
        purpose=model.purpose,
        code_hash=model.code_hash,
        expires_at=model.expires_at,
        consumed_at=model.consumed_at,
        created_at=model.created_at,
    )


class SqlAlchemyVerificationRepository(VerificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_code(
        self, user_id: UUID, purpose: str, code_hash: str, expires_at: datetime
    ) -> VerificationCode:
        model = VerificationCodeModel(
            id=uuid4(), user_id=user_id, purpose=purpose, code_hash=code_hash, expires_at=expires_at
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _to_entity(model)

    async def get_latest_active_code(self, user_id: UUID, purpose: str) -> VerificationCode | None:
        result = await self.session.execute(
            select(VerificationCodeModel)
            .where(
                VerificationCodeModel.user_id == user_id,
                VerificationCodeModel.purpose == purpose,
                VerificationCodeModel.consumed_at.is_(None),
            )
            .order_by(VerificationCodeModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def get_valid_code(
        self, user_id: UUID, purpose: str, code_hash: str
    ) -> VerificationCode | None:
        result = await self.session.execute(
            select(VerificationCodeModel).where(
                VerificationCodeModel.user_id == user_id,
                VerificationCodeModel.purpose == purpose,
                VerificationCodeModel.code_hash == code_hash,
                VerificationCodeModel.consumed_at.is_(None),
            )
        )
        model = result.scalar_one_or_none()
        if model is None or model.expires_at < datetime.now(UTC):
            return None
        return _to_entity(model)

    async def consume_code(self, code_id: UUID) -> None:
        result = await self.session.execute(
            select(VerificationCodeModel).where(VerificationCodeModel.id == code_id)
        )
        model = result.scalar_one_or_none()
        if model is not None:
            model.consumed_at = datetime.now(UTC)
            await self.session.commit()
