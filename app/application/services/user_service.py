from app.application.exceptions import (
    AuthorizationError,
)

from app.domain.entities.user import (
    User,
)

from app.domain.repositories.user_repository import (
    UserRepository,
)

from app.domain.security.authorization import (
    Permission,
    UserRole,
    has_permission,
)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    def get_users(
        self,
        current_user: User,
        page: int,
        page_size: int,
        search: str | None,
        role: UserRole | None,
        is_active: bool | None,
    ) -> dict:
        self._require_permission(
            current_user,
            Permission.USER_READ_ALL,
        )

        normalized_search = self._normalize_search(search)

        (users, total_items) = (
            self.user_repository.get_all(
                page=page,
                page_size=page_size,
                search=normalized_search,
                role=role,
                is_active=is_active,
            )
        )

        total_pages = (
            total_items
            + page_size
            - 1
        ) // page_size

        return {
            "items": users,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        }

    @staticmethod
    def _normalize_search(
        search: str | None,
    ) -> str | None:
        if search is None:
            return None

        normalized_search = search.strip().lower()

        if not normalized_search:
            return None

        return normalized_search


    @staticmethod
    def _require_permission(
        user: User,
        permission: Permission,
    ) -> None:
        if not has_permission(
            user.role,
            permission,
        ):
            raise AuthorizationError(
                "Bu islem icin "
                "yetkiniz yok"
            )
        