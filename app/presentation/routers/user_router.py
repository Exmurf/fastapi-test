from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.application.schemas.user_schema import (
    PaginatedUserResponse,
)

from app.application.services.user_service import (
    UserService,
)

from app.domain.entities.user import (
    User,
)

from app.domain.security.authorization import (
    UserRole,
)

from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)

from app.presentation.dependencies.user_dependencies import (
    get_user_service,
)

from app.presentation.responses import (
    ApiErrorResponse,
    ApiResponse,
    success_response,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get(
    "",
    response_model=(
        ApiResponse[PaginatedUserResponse]
    ),
    responses={
        401:{
            "model": ApiErrorResponse
        },
        403:{
            "model": ApiErrorResponse
        },
    },
)
def get_users(
    page: int = Query(
        default=1,
        ge=1,
        description=(
            "Sayfa numarasi"
        ),
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description=(
            "Sayfa basina "
            "kullanici sayisi"
        ),
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=255,
        description=(
            "Kullanici e-posta "
            "adresinde aranacak "
            "metin"
        ),
    ),
    role: UserRole | None = Query(
        default=None,
        description=(
            "Kullanici rol filtresi"
        ),
    ),
    is_active: bool | None = Query(
        default=None,
        description=(
            "Aktiflik durumu filtresi"
        ),
    ),
    current_user: User = Depends(
        get_current_user
    ),
    service: UserService = Depends(
        get_user_service
    ),
):
    result = service.get_users(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        is_active=is_active,
    )

    return success_response(result)