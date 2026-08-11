import json
from datetime import datetime

from redis.exceptions import RedisError

from app.config import settings
from app.domain.entities.product import Product
from app.domain.entities.product_detail import ProductDetail
from app.domain.repositories.product_cache_repository import (
    ProductCacheRepository,
)
from app.infrastructure.redis_client import redis_client


class RedisProductCacheRepository(
    ProductCacheRepository
):
    KEY_PREFIX = "cache:product"

    def get(
        self,
        public_id: str,
    ) -> Product | None:
        try:
            raw_value = redis_client.get(
                self._key(public_id)
            )
        except RedisError:
            return None

        if raw_value is None:
            return None

        try:
            data = json.loads(raw_value)
            return self._to_entity(data)
        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):
            self.invalidate(public_id)
            return None

    def set(
        self,
        product: Product,
    ) -> None:
        if product.public_id is None:
            return

        data = self._to_dict(product)

        try:
            redis_client.set(
                self._key(product.public_id),
                json.dumps(data),
                ex=settings.product_cache_ttl_seconds,
            )
        except RedisError:
            return

    def invalidate(
        self,
        public_id: str,
    ) -> None:
        try:
            redis_client.delete(
                self._key(public_id)
            )
        except RedisError:
            return

    @classmethod
    def _key(
        cls,
        public_id: str,
    ) -> str:
        return (
            f"{cls.KEY_PREFIX}:"
            f"{public_id}"
        )

    @staticmethod
    def _to_dict(
        product: Product,
    ) -> dict:
        detail = None

        if product.detail is not None:
            detail = {
                "id": product.detail.id,
                "product_id": (
                    product.detail.product_id
                ),
                "description": (
                    product.detail.description
                ),
                "brand": product.detail.brand,
                "warranty_months": (
                    product.detail.warranty_months
                ),
            }

        return {
            "id": product.id,
            "public_id": product.public_id,
            "owner_id": product.owner_id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "created_at": (
                product.created_at.isoformat()
                if product.created_at is not None
                else None
            ),
            "updated_at": (
                product.updated_at.isoformat()
                if product.updated_at is not None
                else None
            ),
            "tags": product.tags,
            "detail": detail,
        }

    @staticmethod
    def _to_entity(
        data: dict,
    ) -> Product:
        detail = None

        if data["detail"] is not None:
            detail_data = data["detail"]

            detail = ProductDetail(
                id=detail_data["id"],
                product_id=(
                    detail_data["product_id"]
                ),
                description=(
                    detail_data["description"]
                ),
                brand=detail_data["brand"],
                warranty_months=(
                    detail_data["warranty_months"]
                ),
            )

        return Product(
            id=data["id"],
            public_id=data["public_id"],
            owner_id=data["owner_id"],
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
            created_at=(
                datetime.fromisoformat(
                    data["created_at"]
                )
                if data["created_at"] is not None
                else None
            ),
            updated_at=(
                datetime.fromisoformat(
                    data["updated_at"]
                )
                if data["updated_at"] is not None
                else None
            ),
            tags=data["tags"],
            detail=detail,
        )