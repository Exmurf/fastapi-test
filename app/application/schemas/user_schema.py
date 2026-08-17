from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)

from app.domain.security.authorization import (
    UserRole,
)


class UserListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    public_id: UUID
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime | None


class PaginatedUserResponse(BaseModel):
    items: list[UserListItemResponse]

    page: int
    page_size: int
    total_items: int
    total_pages: int