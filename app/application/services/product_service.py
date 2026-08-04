from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.application.exceptions import NotFoundError, ValidationError

import math

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
            raise ValidationError("Urun adi bos olamaz")
        if price < 0:
            raise ValidationError("Fiyat negatig olamaz")
        if stock < 0:
            raise ValidationError("Stok negatif olamaz")

        product = Product(
            id = None,
            name = name,
            price = price,
            stock = stock,
        )

        return self.repository.create(product)

    def get_all_products(
        self,
        page: int,
        page_size: int,
        min_price: float | None = None,
        max_price: float | None = None,
        min_stock: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> dict:
        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValidationError(
                "Minimum fiyat maksimum fiyattan buyuk olamaz"
            )

        allowed_sort_fields = {
            "id",
            "name",
            "price",
            "stock",
        }

        if sort_by not in allowed_sort_fields:
            raise ValidationError(
                "Gecersiz siralama alani"
            )

        if sort_order not in {"asc", "desc"}:
            raise ValidationError(
                "Siralama yonu asc veya desc olmalidir"
            )

        if search is not None:
            search = search.strip()

            if not search:
                search = None

        offset = (page - 1) * page_size

        products, total_items = self.repository.get_all(
            min_price=min_price,
            max_price=max_price,
            min_stock=min_stock,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            offset=offset,
            limit=page_size,
        )

        total_pages = math.ceil(total_items/page_size)

        return{
            "items": products,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        }

    def get_product_by_id(self, product_id: int) -> Product | None:
        product = self.repository.get_by_id(product_id)

        if product is None:
            raise NotFoundError("Urun bulunamadi")

        return product

    def update_product(
        self,
        product_id: int,
        name: str,
        price: float,
        stock: int,
    ) -> Product:
        if not name.strip():
            raise ValidationError("Urun adi bos olamaz")
        if price < 0:
            raise ValidationError("Fiyat negatif olamaz")
        if stock < 0:
            raise ValidationError("Stok negatif olamaz")

        existing_product = self.repository.get_by_id(product_id)

        if existing_product is None:
            raise NotFoundError("Urun bulunamadi")

        updated_product = Product(
            id = product_id,
            name = name,
            price = price,
            stock = stock,
        )

        result = self.repository.update(updated_product)

        if result is None:
            raise NotFoundError("Urun guncellenemedi")

        return result

    def delete_product(self, product_id:int) -> bool:

        product = self.repository.get_by_id(product_id)

        if product is None:
            raise NotFoundError("Urun bulunamadi")

        deleted = self.repository.delete(product_id)

        if not deleted:
            raise NotFoundError("Urun silinemedi")