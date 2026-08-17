from app.application.exceptions import (
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from app.application.services.activity_log_service import (
    ActivityLogService,
)
from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)
from app.domain.entities.tag import Tag
from app.domain.entities.user import User
from app.domain.repositories.tag_repository import (
    TagRepository,
)
from app.domain.security.authorization import (
    Permission,
    has_permission,
)


class TagService:
    def __init__(
        self,
        repository: TagRepository,
        activity_log_service: ActivityLogService,
    ):
        self.repository = repository
        self.activity_log_service = (
            activity_log_service
        )

    def get_all_tags(
        self,
        current_user: User,
    ) -> list[Tag]:
        if not has_permission(
            current_user.role,
            Permission.TAG_READ,
        ):
            raise AuthorizationError(
                "Tagleri gormek icin yetkiniz yok"
            )

        return self.repository.get_all()

    def create_tag(
        self,
        name: str,
        current_user: User,
    ) -> Tag:
        if not has_permission(
            current_user.role,
            Permission.TAG_CREATE,
        ):
            raise AuthorizationError(
                "Tag olusturmak icin yetkiniz yok"
            )

        normalized_name = (
            name.strip().lower()
        )

        if not normalized_name:
            raise ValidationError(
                "Tag bos olamaz"
            )

        if len(normalized_name) > 50:
            raise ValidationError(
                "Tag en fazla 50 karakter olabilir"
            )

        existing_tag = (
            self.repository.get_by_name(
                normalized_name
            )
        )

        if existing_tag is not None:
            raise ConflictError(
                "Bu tag zaten mevcut"
            )

        created_tag = (
            self.repository.create(
                Tag(
                    id=None,
                    public_id=None,
                    name=normalized_name,
                )
            )
        )

        self.activity_log_service.log(
            user=current_user,
            action=(
                ActivityAction.TAG_CREATE
            ),
            entity_type=(
                ActivityEntityType.TAG
            ),
            entity_id=(
                created_tag.public_id
            ),
            old_value=None,
            new_value=created_tag,
        )

        return created_tag
