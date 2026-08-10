from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.application.exceptions import NotFoundError
from app.application.services.activity_log_service import ActivityLogService
from app.domain.entities.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_activity_log_repository import (
    SQLAlchemyActivityLogRepository,
)
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.presentation.dependencies.auth_dependencies import get_current_user
from app.presentation.responses import success_response


router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)


def serialize_logs(
    logs: list,
    page: int,
    page_size: int,
    total_items: int,
):
    items = []

    for log in logs:
        items.append(
            {
                "id": log.id,
                "user_public_id": log.user_public_id,
                "action": log.action.value,
                "entity_type": log.entity_type.value,
                "entity_id": log.entity_id,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "created_at": log.created_at,
            }
        )

    return success_response(
        {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
        }
    )


@router.get("/me")
def get_my_activity_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    service = ActivityLogService(
        repository=SQLAlchemyActivityLogRepository(
            db
        )
    )

    logs, total_items = service.get_my_logs(
        current_user=current_user,
        page=page,
        page_size=page_size,
    )

    return serialize_logs(
        logs=logs,
        page=page,
        page_size=page_size,
        total_items=total_items,
    )


@router.get("")
def get_activity_logs(
    user_public_id: str | None = Query(
        default=None
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    target_user = None

    if user_public_id is not None:
        user_repository = SQLAlchemyUserRepository(
            db
        )

        target_user = (
            user_repository.get_by_public_id(
                user_public_id
            )
        )

        if target_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

    service = ActivityLogService(
        repository=SQLAlchemyActivityLogRepository(
            db
        )
    )

    logs, total_items = service.get_all_logs(
        current_user=current_user,
        target_user=target_user,
        page=page,
        page_size=page_size,
    )

    return serialize_logs(
        logs=logs,
        page=page,
        page_size=page_size,
        total_items=total_items,
    )