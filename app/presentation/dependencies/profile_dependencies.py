from fastapi import Depends

from app.application.services.profile_service import (
    ProfileService,
)
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.presentation.dependencies.auth_dependencies import (
    get_profile_repository,
    get_user_repository,
)


def get_profile_service(
    profile_repository: ProfileRepository = Depends(
        get_profile_repository
    ),
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
) -> ProfileService:
    return ProfileService(
        profile_repository=profile_repository,
        user_repository=user_repository,
    )