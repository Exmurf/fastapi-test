from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.application.exceptions import (
    NotFoundError, 
    ValidationError,
    AuthenticationError,
    AuthorizationError,
)
from app.domain.security.authorization import (
    Permission,
    UserRole,
    has_permission,
)
from app.domain.entities.user import User
from app.domain.security.authorization import (
    Permission,
    has_permission,
)
from app.domain.entities.product_detail import (
    ProductDetail,
)
from app.domain.repositories.product_detail_repository import (
    ProductDetailRepository,
)
from app.application.services.activity_log_service import (
    ActivityLogService,
)
from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)

from uuid import UUID
import math

class ProductService:
    def __init__(
        self, 
        repository: ProductRepository,
        detail_repository: ProductDetailRepository,
        activity_log_service: ActivityLogService,
    ):
        self.repository = repository
        self.detail_repository = detail_repository
        self.activity_log_service = activity_log_service


    def create_product(
            self,
            name: str,
            price: float,
            stock: int,
            owner_id: int,
            tags: list[str],
            detail_description: str | None,
            detail_brand: str | None,
            detail_warranty_months: int | None,
            current_user: User,
    ) -> Product:
        if not name.strip():
            raise ValidationError("Urun adi bos olamaz")
        if price < 0:
            raise ValidationError("Fiyat negatig olamaz")
        if stock < 0:
            raise ValidationError("Stok negatif olamaz")

        normalized_tags = self._normalize_tags(
            tags
        )

        product = Product(
            id = None,
            public_id = None,
            owner_id = owner_id,
            name = name.strip(),
            price = price,
            stock = stock,
            tags=normalized_tags,
        )

        created_product = self.repository.create(product)

        if (
            detail_description is not None
            or detail_brand is not None
            or detail_warranty_months is not None
        ):
            if created_product.id is None:
                raise RuntimeError(
                    "Urun internal ID bulunamadi"
                )

            detail = ProductDetail(
                id=None,
                product_id=created_product.id,
                description=detail_description,
                brand=detail_brand,
                warranty_months=(
                    detail_warranty_months
                ),
            )

            self.detail_repository.create(
                detail
            )

        self.activity_log_service.log(
            user=current_user,
            action=ActivityAction.PRODUCT_CREATE,
            entity_type=ActivityEntityType.PRODUCT,
            entity_id=created_product.public_id,
            old_value=None,
            new_value=created_product,
        )

        return self.repository.get_by_public_id(
            public_id=created_product.public_id,
            owner_id=created_product.owner_id,
        )
    
    def get_all_products(
        self,
        page: int,
        current_user: User,
        requested_user_public_id: str | None,
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

        if current_user.public_id is None:
            raise AuthenticationError(
                "Kullanici kimligi bulunamadi"
            )

        can_read_all = has_permission(
            current_user.role,
            Permission.PRODUCT_READ_ALL,
        )

        if can_read_all:
            if requested_user_public_id is None:
                effective_owner_public_id = None
            else:
                try:
                    effective_owner_public_id = str(
                        UUID(requested_user_public_id)
                    )
                except ValueError:
                    raise ValidationError(
                        "Gecersiz kullanici UUID degeri"
                    )
        else:
            effective_owner_public_id = (
                current_user.public_id
            )
        
        

        products_with_owners, total_items = self.repository.get_all(
            owner_public_id=effective_owner_public_id,
            min_price=min_price,
            max_price=max_price,
            min_stock=min_stock,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            offset=offset,
            limit=page_size,
        )

        items = []

        for item in products_with_owners:
            product_item = {
                "public_id": (
                    item.product.public_id
                ),
                "name": item.product.name,
                "price": item.product.price,
                "stock": item.product.stock,
                "created_at": item.product.created_at,
                "tags": item.product.tags,
                "detail": (
                    {
                        "description": (
                            item.product.detail.description
                        ),
                        "brand": (
                            item.product.detail.brand
                        ),
                        "warranty_months": (
                            item.product.detail
                            .warranty_months
                        ),
                    }
                    if item.product.detail is not None
                    else None
                ),
            }

            if can_read_all:
                product_item["owner"] = {
                    "public_id": (
                        item.owner_public_id
                    ),
                    "first_name": item.owner_first_name,
                    "last_name": item.owner_last_name,
                    "email": item.owner_email,
                }

            items.append(product_item)

        total_pages = math.ceil(total_items/page_size)

        return{
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        }

    def get_product_by_id(
        self, 
        public_id: str,
        current_user: User,
    ) -> Product:
        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=Permission.PRODUCT_READ_OWN,
            all_permission=Permission.PRODUCT_READ_ALL,
        )

        product = self.repository.get_by_public_id(
            public_id=public_id,
            owner_id=owner_id,
        )
        
        if product is None:
            raise NotFoundError("Urun bulunamadi")

        return product

    def update_product(
        self,
        public_id: str,
        name: str,
        price: float,
        stock: int,
        tags: list[str],
        current_user: User,
    ) -> Product:
        if name is not None and not name.strip():
            raise ValidationError(
                "Urun adi bos olamaz"
            )

        if price is not None and price < 0:
            raise ValidationError(
                "Fiyat negatif olamaz"
            )

        if stock is not None and stock < 0:
            raise ValidationError(
                "Stok negatif olamaz"
            )


        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=(
                Permission.PRODUCT_UPDATE_OWN
            ),
            all_permission=(
                Permission.PRODUCT_UPDATE_ALL
            ),
        )

        existing_product = self.repository.get_by_public_id(
            public_id=public_id,
            owner_id=owner_id,
        )

        if existing_product is None:
            raise NotFoundError("Urun bulunamadi")


        normalized_tags = (
                    self._normalize_tags(tags)
                    if tags is not None
                    else existing_product.tags
        )

        product = Product(
            id=existing_product.id,
            public_id=existing_product.public_id,
            owner_id=existing_product.owner_id,

            name=(
                name.strip()
                if name is not None
                else existing_product.name
            ),

            price=(
                price
                if price is not None
                else existing_product.price
            ),

            stock=(
                stock
                if stock is not None
                else existing_product.stock
            ),

            created_at=existing_product.created_at,

            tags=(
                self._normalize_tags(tags)
                if tags is not None
                else existing_product.tags
            ),

            detail=existing_product.detail,
        )

        updated_product = self.repository.update(
            product
        )

        if updated_product is None:
            raise NotFoundError(
                "Urun bulunamadi"
            )

        self.activity_log_service.log(
            user=current_user,
            action=(
                ActivityAction.PRODUCT_UPDATE
            ),
            entity_type=(
                ActivityEntityType.PRODUCT
            ),
            entity_id=(
                updated_product.public_id
            ),
            old_value=existing_product,
            new_value=updated_product,
        )

        return updated_product

    def delete_product(
        self, 
        public_id: str,
        current_user: User,
    ) -> bool:
        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=Permission.PRODUCT_DELETE_OWN,
            all_permission=Permission.PRODUCT_DELETE_ALL,
        )

        product = self.repository.get_by_public_id(
            public_id=public_id,
            owner_id=owner_id,
        )

        if product is None:
            raise NotFoundError("Urun bulunamadi")

        deleted = self.repository.delete(
            public_id=public_id,
            owner_id=owner_id,
        )

        if not deleted:
            raise NotFoundError("Urun silinemedi")

        self.activity_log_service.log(
            user=current_user,
            action=ActivityAction.PRODUCT_DELETE,
            entity_type=ActivityEntityType.PRODUCT,
            entity_id=product.public_id,
            old_value=product,
            new_value=None,
        )

        return True

    @staticmethod
    def _resolve_owner_id(
        current_user: User,
        own_permission: Permission,
        all_permission: Permission,
    ) -> int | None:
        if has_permission(
            current_user.role,
            all_permission,
        ):
            return None

        if has_permission(
            current_user.role,
            own_permission,
        ):
            if current_user.id is None:
                raise RuntimeError(
                    "Kullanicinin internal ID "
                    "degeri bulunamadi"
                )

            return current_user.id

        raise AuthorizationError(
            "Bu islem icin yetkiniz yok"
        )

    @staticmethod
    def _normalize_tags(
        tags: list[str],
    ) -> list[str]:
        normalized_tags = []

        for tag in tags:
            normalized_tag = (
                tag.strip().lower()
            )

            if not normalized_tag:
                raise ValidationError(
                    "Tag bos olamaz"
                )

            if len(normalized_tag) > 50:
                raise ValidationError(
                    "Tag en fazla 50 karakter olabilir"
                )

            if normalized_tag in normalized_tags:
                raise ValidationError(
                    "Ayni tag birden fazla kez eklenemez"
                )

            normalized_tags.append(
                normalized_tag
            )

        return normalized_tags