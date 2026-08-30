import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_password, hash_refresh_token
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.verification_repository import VerificationRepository
from app.infrastructure.email.email_sender import send_email

PASSWORD_RESET_PURPOSE = "password_reset"

GENERIC_MESSAGE = "If that email is registered, a password reset code has been sent."


def _generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def _hash_code(code: str) -> str:
    return hash_refresh_token(code)


async def request_password_reset_use_case(
    email: str,
    user_repository: UserRepository,
    verification_repository: VerificationRepository,
) -> str:
    user = await user_repository.get_by_email(email)
    if user is None:
        return GENERIC_MESSAGE

    existing = await verification_repository.get_latest_active_code(user.id, PASSWORD_RESET_PURPOSE)
    if existing is not None:
        seconds_since_created = (datetime.now(UTC) - existing.created_at).total_seconds()
        if seconds_since_created < 60:
            return GENERIC_MESSAGE
        await verification_repository.consume_code(existing.id)

    code = _generate_code()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    await verification_repository.create_code(
        user.id, PASSWORD_RESET_PURPOSE, _hash_code(code), expires_at
    )
    send_email(
        user.email,
        "Reset your Forex Analyst password",
        (
            f"Your password reset code is {code}. It expires in "
            f"{settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes. "
            "If you did not request this, ignore this email."
        ),
    )
    return GENERIC_MESSAGE


async def confirm_password_reset_use_case(
    email: str,
    code: str,
    new_password: str,
    user_repository: UserRepository,
    verification_repository: VerificationRepository,
) -> None:
    user = await user_repository.get_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code"
        )

    valid_code = await verification_repository.get_valid_code(
        user.id, PASSWORD_RESET_PURPOSE, _hash_code(code)
    )
    if valid_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code"
        )

    await verification_repository.consume_code(valid_code.id)
    await user_repository.update_password(user.id, hash_password(new_password))
    await user_repository.revoke_all_refresh_tokens_for_user(user.id)
