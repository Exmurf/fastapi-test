from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.activity_log_service import (
    ActivityLogService,
)
from app.application.services.tag_service import (
    TagService,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_tag_repository import (
    SQLAlchemyTagRepository,
)
from app.presentation.dependencies.activity_log_dependencies import (
    get_activity_log_service,
)


def get_tag_service(
    db: Session = Depends(get_db),
    activity_log_service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> TagService:
    return TagService(
        repository=(
            SQLAlchemyTagRepository(
                db
            )
        ),
        activity_log_service=(
            activity_log_service
        ),
    )
