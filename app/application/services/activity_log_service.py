from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.application.exceptions import (
    AuthorizationError,
)
from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)
from app.domain.entities.activity_log import ActivityLog
from app.domain.entities.user import User
from app.domain.repositories.activity_log_repository import (
    ActivityLogRepository,
)
from app.domain.security.authorization import (
    Permission,
    has_permission,
)




SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "refresh_token",
    "access_token",
    "jwt_secret_key",
}

INTERNAL_FIELDS = {
    "id",
    "user_id",
    "owner_id",
    "product_id",
    "tag_id",
    "updated_at"
}

class ActivityLogService:

    def __init__(
        self,
        repository: ActivityLogRepository,
    ):
        self.repository = repository

    def log(
        self,
        user: User,
        action: ActivityAction,
        entity_type: ActivityEntityType,
        entity_id: str | int | None,
        old_value=None,
        new_value=None,
    ) -> ActivityLog:

        if user.id is None:
            raise RuntimeError(
                "Activity log icin "
                "kullanici ID bulunamadi"
            )

        if user.public_id is None:
            raise RuntimeError(
                "Activity log icin kullanici public ID bulunamadi"
            )

        normalized_old = (
            self._normalize(old_value)
        )

        normalized_new = (
            self._normalize(new_value)
        )

        if (
            normalized_old is not None
            and normalized_new is not None
        ):
            (
                normalized_old,
                normalized_new,
            ) = self._get_changes(
                normalized_old,
                normalized_new,
            )

        activity_log = ActivityLog(
            id=None,
            user_id=user.id,
            action=action,
            entity_type=entity_type,
            entity_id=(
                str(entity_id)
                if entity_id is not None
                else None
            ),
            old_value=normalized_old,
            new_value=normalized_new,
            user_public_id=user.public_id,
        )

        return self.repository.create(
            activity_log
        )

    def get_all_logs(
        self,
        current_user: User,
        page: int,
        page_size: int,
        target_user: User | None = None,
        action: ActivityAction | None = None,
        entity_type: ActivityEntityType | None = None,
        entity_id: str | None = None,
    ) -> tuple[list[ActivityLog], int]:

        if not has_permission(
            current_user.role,
            Permission.ACTIVITY_READ_ALL,
        ):
            raise AuthorizationError(
                "Activity loglarini gormek icin yetkiniz yok"
            )

        user_id = None

        if target_user is not None:
            if target_user.id is None:
                raise RuntimeError(
                    "Hedef kullanici ID bulunamadi"
                )

            user_id = target_user.id

        return self.repository.get_all(
            user_id=user_id,
            page=page,
            page_size=page_size,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    def get_my_logs(
        self,
        current_user: User,
        page: int,
        page_size: int,
        action: ActivityAction | None = None,
        entity_type: ActivityEntityType | None = None,
        entity_id: str | None = None,
    ) -> tuple[list[ActivityLog], int]:

        if current_user.id is None:
            raise RuntimeError(
                "Kullanici ID bulunamadi"
            )

        return self.repository.get_all(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @classmethod
    def _normalize(
        cls,
        value,
    ):

        if value is None:
            return None

        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, BaseModel):
            value = value.model_dump()

        elif is_dataclass(value):
            value = asdict(value)

        if isinstance(value, dict):
            result = {}

            for key, item in value.items():

                if key in SENSITIVE_FIELDS:
                    continue

                if key in INTERNAL_FIELDS:
                    continue

                result[key] = cls._normalize(
                    item
                )

            return result

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                cls._normalize(item)
                for item in value
            ]

        return str(value)

    @staticmethod
    def _get_changes(
        old_value: dict,
        new_value: dict,
    ) -> tuple[dict, dict]:

        changed_old = {}
        changed_new = {}

        keys = (
            set(old_value.keys())
            | set(new_value.keys())
        )

        for key in keys:

            old_item = old_value.get(key)
            new_item = new_value.get(key)

            if old_item == new_item:
                continue

            changed_old[key] = old_item
            changed_new[key] = new_item

        return changed_old, changed_new