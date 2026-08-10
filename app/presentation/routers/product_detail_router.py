from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.application.schemas.product_detail_schema import (
    ProductDetailRequest,
    ProductDetailResponse,
)
from app.application.services.product_detail_service import (
    ProductDetailService,
)
from app.domain.entities.user import User
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.presentation.dependencies.product_detail_dependencies import (
    get_product_detail_service,
)
from app.presentation.responses import (
    ApiResponse,
    success_response,
)


router = APIRouter(
    prefix="/products",
    tags=["Product Details"],
)

@router.post(
    "/{product_public_id}/detail",
    response_model=ApiResponse[
        ProductDetailResponse
    ],
    status_code=status.HTTP_201_CREATED,
)
def create_product_detail(
    product_public_id: UUID,
    detail_data: ProductDetailRequest,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProductDetailService = Depends(
        get_product_detail_service
    ),
):
    detail = service.create_detail(
        product_public_id=str(
            product_public_id
        ),
        description=(
            detail_data.description
        ),
        brand=detail_data.brand,
        warranty_months=(
            detail_data.warranty_months
        ),
        current_user=current_user,
    )

    return success_response(detail)

@router.get(
    "/{product_public_id}/detail",
    response_model=ApiResponse[
        ProductDetailResponse
    ],
)
def get_product_detail(
    product_public_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProductDetailService = Depends(
        get_product_detail_service
    ),
):
    detail = service.get_detail(
        product_public_id=str(
            product_public_id
        ),
        current_user=current_user,
    )

    return success_response(detail)

@router.put(
    "/{product_public_id}/detail",
    response_model=ApiResponse[
        ProductDetailResponse
    ],
)
def update_product_detail(
    product_public_id: UUID,
    detail_data: ProductDetailRequest,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProductDetailService = Depends(
        get_product_detail_service
    ),
):
    detail = service.update_detail(
        product_public_id=str(
            product_public_id
        ),
        description=(
            detail_data.description
        ),
        brand=detail_data.brand,
        warranty_months=(
            detail_data.warranty_months
        ),
        current_user=current_user,
    )

    return success_response(detail)