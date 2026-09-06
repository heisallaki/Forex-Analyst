from datetime import datetime

from pydantic import BaseModel, Field


class UserListItem(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(pattern="^(admin|analyst|viewer)$")


class UpdateUserStatusRequest(BaseModel):
    is_active: bool
