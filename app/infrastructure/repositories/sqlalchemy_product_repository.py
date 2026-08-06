from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.models.product_model import ProductModel

class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        product: Product
    ) -> Product:
        product_model = ProductModel(
            owner_id = product.owner_id,
            name = product.name,
            price = product.price,
            stock = product.stock,
        )

        self.db.add(product_model)
        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def get_all(
        self,
        owner_id: int,
        can_read_all: bool,
        min_price: float | None = None,
        max_price: float | None = None,
        min_stock: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Product], int]:

        query = self.db.query(ProductModel)

        query = query.filter(
            ProductModel.is_deleted.is_(False)
        )

        if not can_read_all:
            query = query.filter(
                ProductModel.owner_id == owner_id
            )

        if search is not None:
            query = query.filter(
                ProductModel.name.ilike(f"%{search}%")
            )

        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        
        if min_stock is not None:
            query = query.filter(ProductModel.stock >= min_stock)

        total_items = query.count()

        sort_columns = {
            "id": ProductModel.id,
            "name": ProductModel.name,
            "price": ProductModel.price,
            "stock": ProductModel.stock,
        }

        sort_column = sort_columns[sort_by]

        if sort_order == "desc":
            sort_expression = sort_column.desc()
        else:
            sort_expression = sort_column.asc()

        if sort_by == "id":
            query = query.order_by(
                sort_expression
            )
        else:
            query = query.order_by(
                sort_expression,
                ProductModel.id.asc(),
            )

        product_models = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        products = [
            self._to_entity(product_model)
            for product_model in product_models
        ]

        return products, total_items

    def get_by_public_id(
        self,
        public_id: str,
        owner_id: int,
    ) -> Product | None:
        product_model = self._get_active_model(
            public_id=public_id,
            owner_id=owner_id,
        )

        if product_model is None:
            return None

        return self._to_entity(product_model)

    def update(
        self,
        product: Product
    ) -> Product | None:
        if product.id is None:
            return None

        product_model = self._get_active_model(
            public_id = product.public_id,
            owner_id = product.owner_id,
        )

        if product_model is None:
            return None

        product_model.name = product.name
        product_model.price = product.price
        product_model.stock = product.stock

        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def delete(
        self, 
        public_id: str,
        owner_id: int,
    ) -> bool:
        product_model = self._get_active_model(
            public_id=public_id,
            owner_id=owner_id,
        )

        if product_model is None:
            return False

        product_model.is_deleted = True

        self.db.commit()

        return True

    def _get_active_model(
        self,
        public_id: str,
        owner_id: int,
    ) -> ProductModel | None:
        return(
            self.db.query(ProductModel)
            .filter(
                ProductModel.public_id == public_id,
                ProductModel.owner_id == owner_id,
                ProductModel.is_deleted.is_(False),
            )
            .first()
        )

    @staticmethod
    def _to_entity(
        product_model: ProductModel
    ) -> Product:
        return Product(
            id = product_model.id,
            public_id=product_model.public_id,
            owner_id=product_model.owner_id,
            name = product_model.name,
            price = product_model.price,
            stock = product_model.stock,
        )


    