import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_refresh_token
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.verification_repository import VerificationRepository
from app.infrastructure.email.email_sender import send_email

EMAIL_VERIFICATION_PURPOSE = "email_verification"


def _generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def _hash_code(code: str) -> str:
    return hash_refresh_token(code)


async def send_verification_code(
    user_id: UUID, email: str, repository: VerificationRepository
) -> None:
    code = _generate_code()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    await repository.create_code(user_id, EMAIL_VERIFICATION_PURPOSE, _hash_code(code), expires_at)
    send_email(
        email,
        "Verify your Forex Analyst account",
        (
            f"Your verification code is {code}. It expires in "
            f"{settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes."
        ),
    )


async def resend_verification_code_use_case(
    user_id: UUID, email: str, repository: VerificationRepository
) -> None:
    existing = await repository.get_latest_active_code(user_id, EMAIL_VERIFICATION_PURPOSE)
    if existing is not None:
        seconds_since_created = (datetime.now(UTC) - existing.created_at).total_seconds()
        if seconds_since_created < 60:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait at least 60 seconds before requesting another code",
            )
        await repository.consume_code(existing.id)
    await send_verification_code(user_id, email, repository)


async def confirm_email_verification_use_case(
    user_id: UUID,
    code: str,
    verification_repository: VerificationRepository,
    user_repository: UserRepository,
) -> None:
    valid_code = await verification_repository.get_valid_code(
        user_id, EMAIL_VERIFICATION_PURPOSE, _hash_code(code)
    )
    if valid_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code"
        )
    await verification_repository.consume_code(valid_code.id)
    await user_repository.mark_verified(user_id)
