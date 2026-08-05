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

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    repository = SQLAlchemyProductRepository(db)
    return ProductService(repository)


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
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ApiErrorResponse},
    },
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
    )

    return success_response(product)


@router.get(
    "",
    response_model=ApiResponse[PaginatedProductResponse],
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
        page=page,
        page_size=page_size,
        min_price=min_price,
        max_price=max_price,
        min_stock=min_stock,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        owner_id=get_current_user_id(current_user)
    )

    return success_response(result)


@router.get(
    "/{product_public_id}",
    response_model=ApiResponse[ProductResponse],
    responses={
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def get_product_by_id(
    product_public_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    product = service.get_product_by_id(
        public_id=str(product_public_id),
        owner_id=get_current_user_id(current_user),
    )

    return success_response(product)


@router.put(
    "/{product_public_id}",
    response_model=ApiResponse[ProductResponse],
    responses={
        400: {"model": ApiErrorResponse},
        401: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def update_product(
    product_public_id: UUID,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    product = service.update_product(
        str(product_public_id),
        product_data.name,
        product_data.price,
        product_data.stock,
        get_current_user_id(current_user),
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
)
def delete_product(
    product_public_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    service.delete_product(
        str(product_public_id),
        get_current_user_id(current_user),
    )

    return success_response(
        {
            "message": "Urun basariyla silindi",
        }
    )