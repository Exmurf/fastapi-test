from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.application.schemas.product_schema import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    PaginatedProductResponse,
)
from app.application.services.product_service import ProductService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)
from app.presentation.responses import (
    ApiErrorResponse,
    ApiResponse,
    success_response,
)

from typing import Literal


router = APIRouter(
    prefix="/products",
    tags=["products"],
)


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    repository = SQLAlchemyProductRepository(db)
    return ProductService(repository)


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
    service: ProductService = Depends(get_product_service),
):
    product = service.create_product(
        product_data.name,
        product_data.price,
        product_data.stock,
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
    )

    return success_response(result)


@router.get(
    "/{product_id}",
    response_model=ApiResponse[ProductResponse],
    responses={
        404: {"model": ApiErrorResponse},
    },
)
def get_product_by_id(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    product = service.get_product_by_id(product_id)

    return success_response(product)


@router.put(
    "/{product_id}",
    response_model=ApiResponse[ProductResponse],
    responses={
        400: {"model": ApiErrorResponse},
        404: {"model": ApiErrorResponse},
    },
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    product = service.update_product(
        product_id,
        product_data.name,
        product_data.price,
        product_data.stock,
    )

    return success_response(product)


@router.delete(
    "/{product_id}",
    response_model=ApiResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ApiErrorResponse},
    },
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    service.delete_product(product_id)

    return success_response(
        {
            "message": "Ürün başarıyla silindi",
        }
    )