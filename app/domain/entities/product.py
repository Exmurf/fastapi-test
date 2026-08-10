from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.product_detail import ProductDetail


@dataclass
class Product:
    id: int | None
    public_id: str | None
    owner_id: int
    name: str
    price: float
    stock: int
    created_at: datetime | None = None
    tags: list[str] = field(
        default_factory=list
    )
    detail: ProductDetail | None = None
    updated_at: datetime | None = None