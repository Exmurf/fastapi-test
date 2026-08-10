from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.read_models.user_analytics import (
    UserAnalytics,
)
from app.domain.repositories.analytics_repository import (
    AnalyticsRepository,
)
from app.infrastructure.models.product_model import (
    ProductModel,
)
from app.infrastructure.models.product_tag_model import (
    product_tags,
)


class SQLAlchemyAnalyticsRepository(
    AnalyticsRepository
):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_user_analytics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> UserAnalytics:

        product_query = (
            self.db.query(ProductModel)
            .filter(
                ProductModel.owner_id == user_id,
                ProductModel.is_deleted.is_(False),
                ProductModel.created_at
                >= start_date,
                ProductModel.created_at
                <= end_date,
            )
        )

        total_products = (
            product_query.count()
        )

        first_product_created_at = (
            product_query
            .with_entities(
                func.min(
                    ProductModel.created_at
                )
            )
            .scalar()
        )

        total_tags = (
            self.db.query(
                func.count()
            )
            .select_from(product_tags)
            .join(
                ProductModel,
                product_tags.c.product_id
                == ProductModel.id,
            )
            .filter(
                ProductModel.owner_id == user_id,
                ProductModel.is_deleted.is_(False),
                ProductModel.created_at
                >= start_date,
                ProductModel.created_at
                <= end_date,
            )
            .scalar()
        )

        return UserAnalytics(
            first_product_created_at=(
                first_product_created_at
            ),
            total_products=total_products,
            total_tags=total_tags or 0,
        )