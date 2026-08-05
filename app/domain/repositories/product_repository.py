from abc import ABC, abstractmethod
from app.domain.entities.product import Product

class ProductRepository(ABC):

    @abstractmethod
    def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_all(
        self,
        owner_id: int,
        min_price: float | None = None,
        max_price: float | None = None,
        min_stock: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Product], int]:
        pass

    @abstractmethod
    def get_by_public_id(
        self, 
        public_id: str,
        owner_id: int,

    ) -> Product | None:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product | None:
        pass

    @abstractmethod
    def delete(
        self, 
        public_id: str,
        owner_id: int,
    ) -> bool:
        pass