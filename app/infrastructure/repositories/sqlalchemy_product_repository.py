from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.models.product_model import ProductModel

class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        product_model = ProductModel(
            name = product.name,
            price = product.price,
            stock = product.stock,
        )

        self.db.add(product_model)
        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def get_all(self) -> list[Product]:
        product_models = self.db.query(ProductModel).all()

        return [
            self._to_entity(product_model)
            for product_model in product_models
        ]

    def get_by_id(self,product_id: int) -> Product | None:
        product_model = self.db.get(ProductModel, product_id)

        if product_model is None:
            return None

        return self._to_entity(product_model)

    def update(self,product: Product) -> Product | None:
        if product.id is None:
            return None

        product_model = self.db.get(ProductModel, product.id)

        if product_model is None:
            return None

        product_model.name = product.name
        product_model.price = product.price
        product_model.stock = product.stock

        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def delete(self, product_id: int) -> bool:
        product_model = self.db.get(ProductModel, product_id)

        if product_model is None:
            return False

        self.db.delete(product_model)
        self.db.commit()

        return True

    @staticmethod
    def _to_entity(product_model: ProductModel) -> Product:
        return Product(
            id = product_model.id,
            name = product_model.name,
            price = product_model.price,
            stock = product_model.stock,
        )


    