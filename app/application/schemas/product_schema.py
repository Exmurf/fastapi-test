from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from datetime import datetime

from app.application.schemas.product_detail_schema import (
    ProductDetailRequest,
    ProductDetailResponse,
)



class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock:int = Field(ge=0)
    tags: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    detail: ProductDetailRequest | None = None

class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    price: float | None = Field(
        default=None,
        ge=0,
    )
    stock: int | None = Field(
        default=None,
        ge=0,
    )
    tags: list[str] | None = Field(
        default=None,
        max_length=20,
    )
    detail: ProductDetailRequest | None = None

class ProductOwnerResponse(BaseModel):
    public_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    name:str
    price:float
    stock:int
    owner: ProductOwnerResponse | None = None
    created_at: datetime | None = None
    tags: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    detail: ProductDetailResponse | None = None

class PaginatedProductResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    
