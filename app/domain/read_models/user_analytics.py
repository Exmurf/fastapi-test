from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserAnalytics:
    first_product_created_at: datetime | None
    total_products: int
    total_tags: int