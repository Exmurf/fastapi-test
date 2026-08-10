from dataclasses import dataclass
from datetime import datetime

from app.domain.security.authorization import UserRole



@dataclass
class User:
    id: int | None
    public_id: str | None
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime | None = None