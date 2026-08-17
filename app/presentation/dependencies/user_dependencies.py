from fastapi import Depends

from app.application.services.activity_log_service import (
    ActivityLogService,
)

from app.application.services.user_service import (
    UserService,
)

from app.domain.repositories.user_repository import (
    UserRepository,
)

from app.presentation.dependencies.activity_log_dependencies import (
    get_activity_log_service,
)

from app.presentation.dependencies.auth_dependencies import (
    get_user_repository,
)


def get_user_service(
    user_repository:
    UserRepository = Depends(
        get_user_repository
    ),

    activity_log_service:
    ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> UserService:
    return UserService(
        user_repository=(
            user_repository
        ),

        activity_log_service=(
            activity_log_service
        ),
    )