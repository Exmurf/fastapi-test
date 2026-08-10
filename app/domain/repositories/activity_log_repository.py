from abc import ABC, abstractmethod

from app.domain.entities.activity_log import (
    ActivityLog,
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
    ) -> tuple[list[ActivityLog], int]:
        pass