from abc import ABC, abstractmethod

from app.domain.entities.product_detail import ProductDetail


class ProductDetailRepository(ABC):

    @abstractmethod
    def create(
        self,
        detail: ProductDetail,
    ) -> ProductDetail:
        pass

    @abstractmethod
    def get_by_product_id(
        self,
        product_id: int,
    ) -> ProductDetail | None:
        pass

    @abstractmethod
    def update(
        self,
        detail: ProductDetail,
    ) -> ProductDetail | None:
        pass