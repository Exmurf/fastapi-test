from abc import ABC, abstractmethod
from app.domain.entities.product import Product

class ProductRepository(ABC):

    @abstractmethod
    def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    def get_all(self) -> list[Product]:
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product | None:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        pass