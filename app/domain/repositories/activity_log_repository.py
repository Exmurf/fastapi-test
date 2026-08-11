from abc import ABC, abstractmethod

from app.domain.entities.activity_log import (
    ActivityLog,
)
from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)



class ActivityLogRepository(ABC):

    @abstractmethod
    def create(
        self,
        activity_log: ActivityLog,
    ) -> ActivityLog:
        pass

    @abstractmethod
    def get_all(
        self,
        user_id: int | None,
        page: int,
        page_size: int,
        action: ActivityAction | None = None,
        entity_type: ActivityEntityType | None = None,
        entity_id: str | None = None,
    ) -> tuple[list[ActivityLog], int]:
        pass