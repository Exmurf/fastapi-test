from sqlalchemy.orm import Session

from app.domain.entities.product_detail import (
    ProductDetail,
)
from app.domain.repositories.product_detail_repository import (
    ProductDetailRepository,
)
from app.infrastructure.models.product_detail_model import (
    ProductDetailModel,
)


class SQLAlchemyProductDetailRepository(
    ProductDetailRepository
):
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        detail: ProductDetail,
    ) -> ProductDetail:
        detail_model = ProductDetailModel(
            product_id=detail.product_id,
            description=detail.description,
            brand=detail.brand,
            warranty_months=(
                detail.warranty_months
            ),
        )

        self.db.add(detail_model)
        self.db.commit()
        self.db.refresh(detail_model)

        return self._to_entity(
            detail_model
        )

    def get_by_product_id(
        self,
        product_id: int,
    ) -> ProductDetail | None:
        detail_model = (
            self.db.query(
                ProductDetailModel
            )
            .filter(
                ProductDetailModel.product_id
                == product_id
            )
            .first()
        )

        if detail_model is None:
            return None

        return self._to_entity(
            detail_model
        )

    def update(
        self,
        detail: ProductDetail,
    ) -> ProductDetail | None:
        detail_model = (
            self.db.query(
                ProductDetailModel
            )
            .filter(
                ProductDetailModel.product_id
                == detail.product_id
            )
            .first()
        )

        if detail_model is None:
            return None

        detail_model.description = (
            detail.description
        )
        detail_model.brand = detail.brand
        detail_model.warranty_months = (
            detail.warranty_months
        )

        self.db.commit()
        self.db.refresh(detail_model)

        return self._to_entity(
            detail_model
        )

    @staticmethod
    def _to_entity(
        detail_model: ProductDetailModel,
    ) -> ProductDetail:
        return ProductDetail(
            id=detail_model.id,
            product_id=detail_model.product_id,
            description=(
                detail_model.description
            ),
            brand=detail_model.brand,
            warranty_months=(
                detail_model.warranty_months
            ),
        )