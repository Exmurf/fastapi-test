from app.application.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)

from app.application.services.activity_log_service import (
    ActivityLogService,
)

from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)

from app.domain.entities.user import User

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
        user_repository:
        UserRepository,
        activity_log_service:
        ActivityLogService,
    ):
        self.user_repository = (
            user_repository
        )

        self.activity_log_service = (
            activity_log_service
        )

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

        normalized_search = (
            self._normalize_search(
                search
            )
        )

        (
            users,
            total_items,
        ) = (
            self.user_repository
            .get_all(
                page=page,
                page_size=page_size,
                search=(
                    normalized_search
                ),
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
            "total_items":
                total_items,
            "total_pages":
                total_pages,
        }

    def delete_user(
        self,
        current_user: User,
        user_public_id: str,
    ) -> User:
        self._require_permission(
            current_user,
            Permission.USER_DELETE_ALL,
        )

        target_user = (
            self.user_repository
            .get_by_public_id(
                user_public_id
            )
        )

        if target_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

        if (
            current_user.public_id
            == target_user.public_id
        ):
            raise ValidationError(
                "Kendi hesabinizi "
                "silemezsiniz"
            )

        if not target_user.is_active:
            return target_user

        updated_user = (
            self.user_repository
            .update_is_active(
                public_id=(
                    user_public_id
                ),
                is_active=False,
            )
        )

        if updated_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

        self.activity_log_service.log(
            user=current_user,
            action=(
                ActivityAction
                .USER_DELETE
            ),
            entity_type=(
                ActivityEntityType.USER
            ),
            entity_id=(
                user_public_id
            ),
            old_value={
                "is_active": True,
            },
            new_value={
                "is_active": False,
            },
        )

        return updated_user

    @staticmethod
    def _normalize_search(
        search: str | None,
    ) -> str | None:
        if search is None:
            return None

        normalized_search = (
            search.strip()
            .lower()
        )

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