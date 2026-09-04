from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, get_user_repository
from app.application.dto.auth_dto import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.dto.verification_dto import (
    ConfirmAccountDeletionRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.application.use_cases.account_deletion import (
    confirm_account_deletion_use_case,
    request_account_deletion_use_case,
)
from app.application.use_cases.authenticate_user import authenticate_user
from app.application.use_cases.email_verification import (
    confirm_email_verification_use_case,
    resend_verification_code_use_case,
)
from app.application.use_cases.logout_user import logout_user
from app.application.use_cases.password_reset import confirm_password_reset_use_case, request_password_reset_use_case
from app.application.use_cases.refresh_token import refresh_access_token
from app.application.use_cases.register_user import register_user
from app.core.rate_limit import limiter
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository_impl import SqlAlchemyUserRepository
from app.infrastructure.repositories.verification_repository_impl import SqlAlchemyVerificationRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def get_verification_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqlAlchemyVerificationRepository:
    return SqlAlchemyVerificationRepository(session)


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/hour")
async def register(
    request: Request,
    payload: RegisterRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> TokenResponse:
    return await register_user(payload, repository, verification_repository)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    return await authenticate_user(payload, repository)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    return await refresh_access_token(payload, repository)


@router.post("/logout", status_code=204)
async def logout(
    payload: RefreshRequest,
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> None:
    await logout_user(payload, repository)


@router.get("/me", response_model=UserResponse)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        permissions=current_user.permissions,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    await confirm_email_verification_use_case(current_user.id, payload.code, verification_repository, user_repository)
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit("5/hour")
async def resend_verification(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    await resend_verification_code_use_case(current_user.id, current_user.email, verification_repository)
    return MessageResponse(message="A new verification code has been sent")


@router.post("/request-account-deletion", response_model=MessageResponse)
@limiter.limit("5/hour")
async def request_account_deletion(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    await request_account_deletion_use_case(current_user.id, current_user.email, verification_repository)
    return MessageResponse(message="A confirmation code has been sent to your email")


@router.post("/confirm-account-deletion", response_model=MessageResponse)
async def confirm_account_deletion(
    payload: ConfirmAccountDeletionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    await confirm_account_deletion_use_case(current_user.id, payload.code, verification_repository, user_repository)
    return MessageResponse(message="Account permanently deleted")


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("5/hour")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    message = await request_password_reset_use_case(payload.email, user_repository, verification_repository)
    return MessageResponse(message=message)


@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("10/hour")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    verification_repository: Annotated[SqlAlchemyVerificationRepository, Depends(get_verification_repository)],
) -> MessageResponse:
    await confirm_password_reset_use_case(
        payload.email, payload.code, payload.new_password, user_repository, verification_repository
    )
    return MessageResponse(message="Password reset successfully. Please log in with your new password.")