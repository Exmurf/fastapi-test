from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
)


class UserAnalyticsResponse(BaseModel):
    user_public_id: UUID
    email: EmailStr

    registered_at: datetime

    first_product_created_at: (
        datetime | None
    )

    total_products: int
    total_tags: int

    average_products_per_day: float

    start_date: datetime
    end_date: datetime