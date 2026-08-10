from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.application.schemas.profile_schema import (
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.application.services.profile_service import (
    ProfileService,
)
from app.domain.entities.user import User
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.presentation.dependencies.profile_dependencies import (
    get_profile_service,
)
from app.presentation.responses import (
    ApiErrorResponse,
    ApiResponse,
    success_response,
)


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)

@router.get(
    "/me",
    response_model=ApiResponse[ProfileResponse],
    responses = {
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def get_own_profile(
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):
    profile = service.get_own_profile(
        current_user=current_user
    )

    return success_response(profile)

@router.put(
    "/me",
    response_model=ApiResponse[ProfileResponse],
    responses={
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def update_own_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):
    profile = service.update_own_profile(
        current_user=current_user,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        bio=profile_data.bio,
    )

    return success_response(profile)

@router.get(
    "/{user_public_id}",
    response_model=ApiResponse[ProfileResponse],
    responses= {
        401: {"model": ApiErrorResponse},
        403: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def get_user_profile(
    user_public_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):
    profile = service.get_user_profile(
        current_user=current_user,
        user_public_id=str(user_public_id),
    )

    return success_response(profile)

@router.put(
    "/{user_public_id}",
    response_model=ApiResponse[ProfileResponse],
    responses={
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse},
        403: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def update_user_profile(
    user_public_id: UUID,
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):
    profile = service.update_user_profile(
        current_user=current_user,
        user_public_id=str(user_public_id),
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        bio=profile_data.bio,
    )

    return success_response(profile)