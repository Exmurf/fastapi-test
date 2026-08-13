from abc import ABC, abstractmethod

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
    ) -> tuple[list[User], int]:
        pass