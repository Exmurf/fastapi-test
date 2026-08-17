from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.user import User
from app.domain.security.authorization import UserRole


class UserRepository(ABC):
    @abstractmethod
    def create(
        self,
        user: User,
    ) -> User:
        pass

    @abstractmethod
    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        pass

    @abstractmethod
    def get_by_public_id(
        self,
        public_id: str,
    ) -> User | None:
        pass

    @abstractmethod
    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        pass

    @abstractmethod
    def get_all(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        is_deleted: bool | None = None,
    ) -> tuple[list[User], int]:
        pass

    @abstractmethod
    def update_is_active(
        self,
        public_id: str,
        is_active: bool,
    ) -> User | None:
        pass

    @abstractmethod
    def soft_delete(
        self,
        public_id: str,
        deleted_email: str,
        deleted_at: datetime,
    ) -> User | None:
        pass
