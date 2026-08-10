from dataclasses import dataclass


@dataclass
class ProductDetail:
    id: int | None
    product_id: int
    description: str | None
    brand: str | None
    warranty_months: int | None