from datetime import datetime, timezone

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
        is_deleted: bool | None,
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
                is_deleted=is_deleted,
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

    def update_user_active(
        self,
        current_user: User,
        user_public_id: str,
        is_active: bool,
    ) -> User:
        self._require_permission(
            current_user,
            Permission.USER_UPDATE_ALL,
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
                "Kendi hesap durumunuzu "
                "degistiremezsiniz"
            )

        if target_user.is_deleted:
            raise ValidationError(
                "Silinmis kullanicinin "
                "aktiflik durumu degistirilemez"
            )

        if target_user.is_active == is_active:
            return target_user

        updated_user = (
            self.user_repository
            .update_is_active(
                public_id=user_public_id,
                is_active=is_active,
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
                .USER_STATUS_UPDATE
            ),
            entity_type=(
                ActivityEntityType.USER
            ),
            entity_id=user_public_id,
            old_value={
                "is_active": (
                    target_user.is_active
                ),
            },
            new_value={
                "is_active": is_active,
            },
        )

        return updated_user

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

        if target_user.is_deleted:
            return target_user

        deleted_at = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)
        deleted_email = (
            self._build_deleted_email(
                target_user,
                deleted_at,
            )
        )

        updated_user = (
            self.user_repository
            .soft_delete(
                public_id=(
                    user_public_id
                ),
                deleted_email=(
                    deleted_email
                ),
                deleted_at=deleted_at,
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
                "email": target_user.email,
                "is_active": (
                    target_user.is_active
                ),
                "is_deleted": False,
            },
            new_value={
                "email": deleted_email,
                "is_active": (
                    target_user.is_active
                ),
                "is_deleted": True,
                "deleted_at": (
                    deleted_at.isoformat()
                ),
            },
        )

        return updated_user

    @staticmethod
    def _build_deleted_email(
        user: User,
        deleted_at: datetime,
    ) -> str:
        local_part, separator, domain = (
            user.email.partition("@")
        )

        if separator == "":
            domain = "deleted.invalid"

        public_id_suffix = (
            user.public_id or "unknown"
        )[:8]
        timestamp = deleted_at.strftime(
            "%Y%m%d%H%M%S"
        )
        suffix = (
            f"+deleted-{timestamp}-"
            f"{public_id_suffix}"
        )
        max_local_length = max(
            1,
            254
            - len(domain)
            - 1
            - len(suffix),
        )

        return (
            f"{local_part[:max_local_length]}"
            f"{suffix}@{domain}"
        )

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
