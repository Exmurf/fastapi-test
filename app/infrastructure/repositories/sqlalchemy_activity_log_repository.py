from sqlalchemy.orm import Session

from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)
from app.domain.entities.activity_log import (
    ActivityLog,
)
from app.domain.repositories.activity_log_repository import (
    ActivityLogRepository,
)
from app.infrastructure.models.activity_log_model import (
    ActivityLogModel,
)
from app.infrastructure.models.user_model import UserModel



class SQLAlchemyActivityLogRepository(
    ActivityLogRepository
):

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        activity_log: ActivityLog,
    ) -> ActivityLog:

        model = ActivityLogModel(
            user_id=activity_log.user_id,
            action=activity_log.action.value,
            entity_type=(
                activity_log.entity_type.value
            ),
            entity_id=activity_log.entity_id,
            old_value=activity_log.old_value,
            new_value=activity_log.new_value,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(
            model,
            user_public_id=activity_log.user_public_id,
        )

    def get_all(
        self,
        user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ActivityLog], int]:

        query = self.db.query(
            ActivityLogModel,
            UserModel,
        ).join(
            UserModel,
            ActivityLogModel.user_id == UserModel.id,
        )

        if user_id is not None:
            query = query.filter(
                ActivityLogModel.user_id
                == user_id
            )

        total_items = query.count()

        models = (
            query
            .order_by(
                ActivityLogModel.created_at.desc()
            )
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
            .all()
        )

        logs = []

        for activity_model, user_model in models:
            logs.append(
                self._to_entity(
                    activity_model,
                    user_public_id=user_model.public_id,
                )
            )

        return logs, total_items

    @staticmethod
    def _to_entity(
        model: ActivityLogModel,
        user_public_id: str | None = None,
    ) -> ActivityLog:

        return ActivityLog(
            id=model.id,
            user_id=model.user_id,
            action=ActivityAction(
                model.action
            ),
            entity_type=ActivityEntityType(
                model.entity_type
            ),
            entity_id=model.entity_id,
            old_value=model.old_value,
            new_value=model.new_value,
            created_at=model.created_at,
            user_public_id=user_public_id,
        )