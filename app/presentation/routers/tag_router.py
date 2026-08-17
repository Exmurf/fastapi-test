from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.application.schemas.tag_schema import (
    TagCreate,
    TagResponse,
)
from app.application.services.tag_service import (
    TagService,
)
from app.domain.entities.user import User
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.presentation.dependencies.tag_dependencies import (
    get_tag_service,
)
from app.presentation.responses import (
    ApiErrorResponse,
    ApiResponse,
    success_response,
)


router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.get(
    "",
    response_model=(
        ApiResponse[
            list[TagResponse]
        ]
    ),
    responses={
        401: {
            "model": ApiErrorResponse
        },
        403: {
            "model": ApiErrorResponse
        },
    },
)
def get_tags(
    current_user: User = Depends(
        get_current_user
    ),
    service: TagService = Depends(
        get_tag_service
    ),
):
    tags = service.get_all_tags(
        current_user=current_user
    )

    return success_response(
        tags
    )


@router.post(
    "",
    response_model=(
        ApiResponse[TagResponse]
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
    responses={
        400: {
            "model": ApiErrorResponse
        },
        401: {
            "model": ApiErrorResponse
        },
        403: {
            "model": ApiErrorResponse
        },
        409: {
            "model": ApiErrorResponse
        },
    },
)
def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(
        get_current_user
    ),
    service: TagService = Depends(
        get_tag_service
    ),
):
    tag = service.create_tag(
        name=tag_data.name,
        current_user=current_user,
    )

    return success_response(
        tag
    )
