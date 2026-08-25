from app.application.dto.auth_dto import RefreshRequest
from app.core.security import hash_refresh_token
from app.domain.repositories.user_repository import UserRepository


async def logout_user(payload: RefreshRequest, repository: UserRepository) -> None:
    token_hash = hash_refresh_token(payload.refresh_token)
    await repository.revoke_refresh_token(token_hash)
