from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

DEFAULT_PERMISSIONS: dict[str, dict[str, bool]] = {
    "admin": {
        "manage_users": True,
        "view_markets": True,
        "manage_strategies": True,
        "execute_trades": True,
        "view_reports": True,
    },
    "analyst": {
        "manage_users": False,
        "view_markets": True,
        "manage_strategies": True,
        "execute_trades": False,
        "view_reports": True,
    },
    "viewer": {
        "manage_users": False,
        "view_markets": True,
        "manage_strategies": False,
        "execute_trades": False,
        "view_reports": True,
    },
}


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    role: str
    permissions: dict
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def default_permissions_for_role(role: str) -> dict:
        return dict(DEFAULT_PERMISSIONS.get(role, DEFAULT_PERMISSIONS["viewer"]))
