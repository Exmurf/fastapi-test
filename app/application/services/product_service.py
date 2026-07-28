from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(
            self,
            name: str,
            price: float,
            stock: int,
    ) -> Product:
        if not name.strip():
            raise ValueError("Urun adi bos olamaz")
        if price < 0:
            raise ValueError("Fiyat negatig olamaz")
        if stock < 0:
            raise ValueError("Stok negatif olamaz")

        product = Product(
            id = None,
            name = name,
            price = price,
            stock = stock,
        )

        return self.repository.create(product)

    def get_all_products(self) -> list[Product]:
        return self.repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        product = self.repository.get_by_id(product_id)

        if product is None:
            raise ValueError("Urun bulunamadi")

        return product

    def update_product(
        self,
        product_id: int,
        name: str,
        price: float,
        stock: int,
    ) -> Product:
        if not name.strip():
            raise ValueError("Urun adi bos olamaz")
        if price < 0:
            raise ValueError("Fiyat negatif olamaz")
        if stock < 0:
            raise ValueError("Stok negatif olamaz")

        existing_product = self.repository.get_by_id(product_id)

        if existing_product is None:
            raise ValueError("Urun bulunamadi")

        updated_product = Product(
            id = product_id,
            name = name,
            price = price,
            stock = stock,
        )

        result = self.repository.update(updated_product)

        if result is None:
            raise ValueError("Urun guncellenemedi")

        return result

    def delete_product(self, product_id:int) -> bool:

        product = self.repository.get_by_id(product_id)

        if product is None:
            raise ValueError("Urun bulunamadi")

        deleted = self.repository.delete(product_id)

        if not deleted:
            raise ValueError("Urun silinemedi")