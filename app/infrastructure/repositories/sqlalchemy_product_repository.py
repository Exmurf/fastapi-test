from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.models.product_model import (
    ProductModel,
)
from app.domain.read_models.product_with_owner import (
    ProductWithOwner,
)
from app.infrastructure.models.user_model import (
    UserModel,
)
from app.infrastructure.models.profile_model import (
    ProfileModel,
)
from app.infrastructure.models.tag_model import TagModel
from app.domain.entities.product_detail import (
    ProductDetail,
)



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

        product_model.tags = (
            self._get_tag_models(
                product.tags
            )
        )

        self.db.add(product_model)
        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def get_all(
        self,
        owner_public_id: str | None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_stock: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[list[Product], int]:

        query = (
            self.db.query(
                ProductModel,
                UserModel,
                ProfileModel,
            )
            .join(
                UserModel,
                ProductModel.owner_id == UserModel.id,
            )
            .outerjoin(
                ProfileModel,
                ProfileModel.user_id == UserModel.id,
            )
            .filter(
                ProductModel.is_deleted.is_(False)
            )
        )

        if owner_public_id is not None:
            query = query.filter(
                UserModel.public_id
                == owner_public_id
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

        rows = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        products_with_owners = []

        for (
            product_model, 
            user_model,
            profile_model,
        ) in rows:
            products_with_owners.append(
                ProductWithOwner(
                    product=self._to_entity(
                        product_model
                    ),
                    owner_public_id=(
                        user_model.public_id
                    ),
                    owner_first_name=(
                        profile_model.first_name
                        if profile_model is not None
                        else None
                    ),
                    owner_last_name=(
                        profile_model.last_name
                        if profile_model is not None
                        else None
                    ),
                    owner_email=user_model.email,
                )
            )

        return products_with_owners, total_items

    def get_by_public_id(
        self,
        public_id: str,
        owner_id: int | None,
    ) -> Product | None:
        query = (
            self.db.query(ProductModel)
            .filter(
                ProductModel.public_id == public_id,
                ProductModel.is_deleted.is_(False),
            )
        )

        if owner_id is not None:
            query = query.filter(
                ProductModel.owner_id == owner_id
            )

        product_model = query.first()

        if product_model is None:
            return None

        return self._to_entity(product_model)

    def update(
        self,
        product: Product,
    ) -> Product | None:
        query = (
            self.db.query(ProductModel)
            .filter(
                ProductModel.public_id
                == product.public_id,
                ProductModel.is_deleted.is_(False),
            )
        )

    

        product_model = query.first()

        if product_model is None:
            return None

        product_model.name = product.name
        product_model.price = product.price
        product_model.stock = product.stock

        product_model.tags = (
            self._get_tag_models(
                product.tags
            )
        )

        self.db.commit()
        self.db.refresh(product_model)

        return self._to_entity(product_model)

    def delete(
        self, 
        public_id: str,
        owner_id: int | None,
    ) -> bool:
        query = (
            self.db.query(ProductModel)
            .filter(
                ProductModel.public_id == public_id,
                ProductModel.is_deleted.is_(False),
            )
        )

        if owner_id is not None:
            query = query.filter(
                ProductModel.owner_id == owner_id
            )

        product_model = query.first()

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
            created_at = product_model.created_at,
            tags=[
                tag_model.name
                for tag_model
                in product_model.tags
            ],
            detail = (
                ProductDetail(
                    id=product_model.detail.id,
                    product_id=product_model.detail.product_id,
                    description=product_model.detail.description,
                    brand=product_model.detail.brand,
                    warranty_months=product_model.detail.warranty_months,
                )
                if product_model.detail is not None
                else None
            ),
            updated_at=product_model.updated_at,
        )

    def _get_tag_models(
        self,
        tag_names: list[str],
    ) -> list[TagModel]:
        tag_models = []

        for tag_name in tag_names:
            tag_model = (
                self.db.query(TagModel)
                .filter(
                    TagModel.name
                    == tag_name
                )
                .first()
            )

            if tag_model is None:
                tag_model = TagModel(
                    name=tag_name
                )

                self.db.add(tag_model)

            tag_models.append(tag_model)

        return tag_models


        