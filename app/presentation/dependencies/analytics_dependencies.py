from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.analytics_service import (
    AnalyticsService,
)
from app.infrastructure.database import (
    get_db,
)
from app.infrastructure.repositories.sqlalchemy_analytics_repository import (
    SQLAlchemyAnalyticsRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


def get_analytics_service(
    db: Session = Depends(get_db),
) -> AnalyticsService:
    return AnalyticsService(
        analytics_repository=(
            SQLAlchemyAnalyticsRepository(db)
        ),
        user_repository=(
            SQLAlchemyUserRepository(db)
        ),
    )