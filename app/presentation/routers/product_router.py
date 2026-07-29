from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.schemas.product_schema import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

from app.application.services.product_service import ProductService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
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

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    try:
        return service.create_product(
            name = product_data.name,
            price = product_data.price,
            stock = product_data.stock,
        )
    except ValueError as error:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(error),
        ) from error

@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_all_products(
    service: ProductService = Depends(get_product_service),
):
    return service.get_all_products()

def get_product_by_id(
        product_id: int,
        service: ProductService = Depends(get_product_service),
):
    try:
        return service.get_product_by_id(product_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = str(error),
        ) from error


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        return service.update_product(
            product_id=product_id,
            name=product_data.name,
            price=product_data.price,
            stock=product_data.stock,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    try:
        service.delete_product(product_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error