from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.product_detail_service import (
    ProductDetailService,
)
from app.infrastructure.database import (
    get_db,
)
from app.infrastructure.repositories.sqlalchemy_product_detail_repository import (
    SQLAlchemyProductDetailRepository,
)
from app.infrastructure.repositories.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)


def get_product_detail_service(
    db: Session = Depends(get_db),
) -> ProductDetailService:
    return ProductDetailService(
        detail_repository=(
            SQLAlchemyProductDetailRepository(
                db
            )
        ),
        product_repository=(
            SQLAlchemyProductRepository(db)
        ),
    )