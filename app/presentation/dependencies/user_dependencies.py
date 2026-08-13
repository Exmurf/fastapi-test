from fastapi import Depends

from app.application.services.user_service import (
    UserService,
)

from app.domain.repositories.user_repository import (
    UserRepository,
)

from app.presentation.dependencies.auth_dependencies import (
    get_user_repository,
)


def get_user_service(
    user_repository: UserRepository = Depends(
        get_user_repository
    )
)-> UserService:
    return UserService(
        user_repository=user_repository
    )

