from pydantic import (
    BaseModel,
    Field,
)


class ProductDetailRequest(BaseModel):
    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    brand: str | None = Field(
        default=None,
        max_length=100,
    )

    warranty_months: int | None = Field(
        default=None,
        ge=0,
    )


class ProductDetailResponse(BaseModel):
    description: str | None
    brand: str | None
    warranty_months: int | None