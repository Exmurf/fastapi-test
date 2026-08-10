from dataclasses import dataclass

from app.domain.entities.product import Product

@dataclass
class ProductWithOwner:
    product: Product
    owner_public_id: str
    owner_first_name: str | None
    owner_last_name: str | None
    owner_email: str