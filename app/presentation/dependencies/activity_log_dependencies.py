from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.activity_log_service import (
    ActivityLogService,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_activity_log_repository import (
    SQLAlchemyActivityLogRepository,
)


def get_activity_log_service(
    db: Session = Depends(get_db),
) -> ActivityLogService:
    repository = SQLAlchemyActivityLogRepository(
        db
    )

    return ActivityLogService(
        repository=repository
    )