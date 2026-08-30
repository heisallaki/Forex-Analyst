import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_refresh_token
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.verification_repository import VerificationRepository
from app.infrastructure.email.email_sender import send_email

ACCOUNT_DELETION_PURPOSE = "account_deletion"


def _generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def _hash_code(code: str) -> str:
    return hash_refresh_token(code)


async def request_account_deletion_use_case(
    user_id: UUID, email: str, repository: VerificationRepository
) -> None:
    code = _generate_code()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    await repository.create_code(user_id, ACCOUNT_DELETION_PURPOSE, _hash_code(code), expires_at)
    send_email(
        email,
        "Confirm Forex Analyst account deletion",
        f"Your account deletion confirmation code is {code}. It expires in "(
            f"{settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes. "
            "If you did not request this, ignore this email."
        ),
    )


async def confirm_account_deletion_use_case(
    user_id: UUID,
    code: str,
    verification_repository: VerificationRepository,
    user_repository: UserRepository,
) -> None:
    valid_code = await verification_repository.get_valid_code(
        user_id, ACCOUNT_DELETION_PURPOSE, _hash_code(code)
    )
    if valid_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired confirmation code"
        )
    await verification_repository.consume_code(valid_code.id)
    await user_repository.delete_user(user_id)
