from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.read_models.user_analytics import (
    UserAnalytics,
)


class AnalyticsRepository(ABC):

    @abstractmethod
    def get_user_analytics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> UserAnalytics:
        pass