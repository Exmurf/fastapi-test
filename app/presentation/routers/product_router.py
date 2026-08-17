from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.application.exceptions import AuthenticationError
from app.application.schemas.product_schema import (
    PaginatedProductResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.application.services.product_service import ProductService
from app.domain.entities.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.presentation.responses import (
    ApiErrorResponse,
    ApiResponse,
    success_response,
)
from app.infrastructure.repositories.sqlalchemy_product_detail_repository import (
    SQLAlchemyProductDetailRepository,
)
from app.presentation.dependencies.rate_limit_dependencies import (
    PRODUCT_READ_LIMIT,
    PRODUCT_READ_WINDOW_SECONDS,
    PRODUCT_WRITE_LIMIT,
    PRODUCT_WRITE_WINDOW_SECONDS,
    user_rate_limit,
)
from app.application.services.activity_log_service import (
    ActivityLogService,
)
from app.presentation.dependencies.activity_log_dependencies import (
    get_activity_log_service,
)
from app.infrastructure.repositories.redis_product_cache_repository import (
    RedisProductCacheRepository,
)
from app.infrastructure.repositories.sqlalchemy_tag_repository import (
    SQLAlchemyTagRepository,
)


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


def get_product_service(
    db: Session = Depends(get_db),
    activity_log_service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> ProductService:
    repository = SQLAlchemyProductRepository(db)

    cache_repository = (
        RedisProductCacheRepository()
    )

    return ProductService(
        repository=repository,
        detail_repository=(
            SQLAlchemyProductDetailRepository(db)
        ),
        activity_log_service=(
            activity_log_service
        ),
        cache_repository=cache_repository,
        tag_repository=(
            SQLAlchemyTagRepository(
                db
            )
        ),
    )


def get_current_user_id(
        current_user: User,
) -> int:
    if current_user.id is None:
        raise RuntimeError(
            "Kullanicinin internal ID degeri yok"
        )
    return current_user.id

@router.post(
    "",
    response_model=ApiResponse[ProductResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ApiErrorResponse},
    },
    dependencies=[
        Depends(
            user_rate_limit(
                bucket="products_write",
                limit=PRODUCT_WRITE_LIMIT,
                window_seconds=(
                    PRODUCT_WRITE_WINDOW_SECONDS
                ),
            )
        ),
    ],
)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    
    product = service.create_product(
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
        owner_id=get_current_user_id(
            current_user
        ),
        tags=product_data.tags,
        detail_description=(
            product_data.detail.description
            if product_data.detail is not None
            else None
        ),
        detail_brand=(
            product_data.detail.brand
            if product_data.detail is not None
            else None
        ),
        detail_warranty_months=(
            product_data.detail.warranty_months
            if product_data.detail is not None
            else None
        ),
        current_user=current_user,
    )



    return success_response(product)


@router.get(
    "",
    response_model=ApiResponse[PaginatedProductResponse],
    response_model_exclude_none=True,
    dependencies=[
        Depends(
            user_rate_limit(
                bucket="products_read",
                limit=PRODUCT_READ_LIMIT,
                window_seconds=(
                    PRODUCT_READ_WINDOW_SECONDS
                ),
            )
        )
    ],
)
def get_all_products(
    page: int = Query(
        default=1,
        ge=1,
        description="Sayfa numarasi",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Sayfa basina urun sayisi",
    ),
    user_public_id: str | None = Query(
        default=None,
        description=(
            "Admin kullanicilar icin "
            "urun sahibi kullanicinin UUID degeri"
        ),
    ),
    min_price: float | None = Query(
        default=None,
        ge=0,
        description="Minimum urun fiyati",
    ),
    max_price: float | None = Query(
            default=None,
            ge=0,
            description="Maksimum urun fiyati",
    ),
    min_stock: int | None = Query(
            default=None,
            ge=0,
            description="Minimum stok miktari",
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Urun adinda aranacak metin"
    ),
    sort_by: Literal[
        "id",
        "name",
        "price",
        "stock",
    ] = Query(
        default="id",
        description="Siralama alani",
    ),
    sort_order: Literal[
        "asc",
        "desc",
    ] = Query(
        default="asc",
        description="Siralama yonu",
    ),
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user),
):
    result = service.get_all_products(
        current_user=current_user,
        requested_user_public_id= user_public_id,
        page=page,
        page_size=page_size,
        min_price=min_price,
        max_price=max_price,
        min_stock=min_stock,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return success_response(result)


@router.get(
    "/{product_public_id}",
    response_model=ApiResponse[ProductResponse],
    response_model_exclude_none=True,
    responses={
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
    dependencies=[
        Depends(
            user_rate_limit(
                bucket="products_read",
                limit=PRODUCT_READ_LIMIT,
                window_seconds=(
                    PRODUCT_READ_WINDOW_SECONDS
                ),
            )
        )
    ],
)
def get_product_by_id(
    product_public_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    product = service.get_product_by_id(
        public_id=str(product_public_id),
        current_user=current_user,
    )

    return success_response(product)


@router.patch(
    "/{product_public_id}",
    response_model=ApiResponse[ProductResponse],
    response_model_exclude_none=True,
    responses={
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
    dependencies=[
        Depends(
            user_rate_limit(
                bucket="products_write",
                limit=PRODUCT_WRITE_LIMIT,
                window_seconds=(
                    PRODUCT_WRITE_WINDOW_SECONDS
                ),
            )
        )
    ],
)
def update_product(
    product_public_id: UUID,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    product = service.update_product(
        public_id=str(product_public_id),
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
        tags=product_data.tags,
        current_user=current_user,
    )

    return success_response(product)


@router.delete(
    "/{product_public_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
    dependencies=[
        Depends(
            user_rate_limit(
                bucket="products_write",
                limit=PRODUCT_WRITE_LIMIT,
                window_seconds=(
                    PRODUCT_WRITE_WINDOW_SECONDS
                ),
            )
        )
    ],
)
def delete_product(
    product_public_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    service.delete_product(
        str(product_public_id),
        current_user,
    )

    return success_response(
        {
            "message": "Urun basariyla silindi",
        }
    )
