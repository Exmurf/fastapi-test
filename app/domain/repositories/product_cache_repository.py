from abc import ABC, abstractmethod

from app.domain.entities.product import Product


class ProductCacheRepository(ABC):

    @abstractmethod
    def get(
        self,
        public_id: str,
    ) -> Product | None:
        pass

    @abstractmethod
    def set(
        self,
        product: Product,
    ) -> None:
        pass

    @abstractmethod
    def invalidate(
        self,
        public_id: str,
    ) -> None:
        pass