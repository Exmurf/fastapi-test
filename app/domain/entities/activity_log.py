from dataclasses import dataclass
from datetime import datetime

from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)


@dataclass
class ActivityLog:
    id: int | None
    user_id: int
    action: ActivityAction
    entity_type: ActivityEntityType
    entity_id: str | None
    old_value: dict | None
    new_value: dict | None
    created_at: datetime | None = None
    user_public_id: str | None = None