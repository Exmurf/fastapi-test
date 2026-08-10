from app.application.exceptions import (
    NotFoundError,
    ValidationError,
)
from app.domain.entities.product_detail import (
    ProductDetail,
)
from app.domain.entities.user import User
from app.domain.repositories.product_detail_repository import (
    ProductDetailRepository,
)
from app.domain.repositories.product_repository import (
    ProductRepository,
)
from app.domain.security.authorization import (
    Permission,
    has_permission,
)


class ProductDetailService:
    def __init__(
        self,
        detail_repository: ProductDetailRepository,
        product_repository: ProductRepository,
    ):
        self.detail_repository = (
            detail_repository
        )
        self.product_repository = (
            product_repository
        )

    def create_detail(
        self,
        product_public_id: str,
        description: str | None,
        brand: str | None,
        warranty_months: int | None,
        current_user: User,
    ) -> ProductDetail:
        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=(
                Permission.PRODUCT_UPDATE_OWN
            ),
            all_permission=(
                Permission.PRODUCT_UPDATE_ALL
            ),
        )

        product = (
            self.product_repository
            .get_by_public_id(
                public_id=product_public_id,
                owner_id=owner_id,
            )
        )

        if product is None:
            raise NotFoundError(
                "Urun bulunamadi"
            )

        if product.id is None:
            raise RuntimeError(
                "Urun internal ID bulunamadi"
            )

        existing_detail = (
            self.detail_repository
            .get_by_product_id(
                product.id
            )
        )

        if existing_detail is not None:
            raise ValidationError(
                "Bu urunun zaten detay kaydi var"
            )

        detail = ProductDetail(
            id=None,
            product_id=product.id,
            description=self._normalize_text(
                description
            ),
            brand=self._normalize_text(
                brand
            ),
            warranty_months=(
                warranty_months
            ),
        )

        return self.detail_repository.create(
            detail
        )

    def get_detail(
        self,
        product_public_id: str,
        current_user: User,
    ) -> ProductDetail:
        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=(
                Permission.PRODUCT_READ_OWN
            ),
            all_permission=(
                Permission.PRODUCT_READ_ALL
            ),
        )

        product = (
            self.product_repository
            .get_by_public_id(
                public_id=product_public_id,
                owner_id=owner_id,
            )
        )

        if product is None:
            raise NotFoundError(
                "Urun bulunamadi"
            )

        if product.id is None:
            raise RuntimeError(
                "Urun internal ID bulunamadi"
            )

        detail = (
            self.detail_repository
            .get_by_product_id(
                product.id
            )
        )

        if detail is None:
            raise NotFoundError(
                "Urun detayi bulunamadi"
            )

        return detail

    def update_detail(
        self,
        product_public_id: str,
        description: str | None,
        brand: str | None,
        warranty_months: int | None,
        current_user: User,
    ) -> ProductDetail:
        owner_id = self._resolve_owner_id(
            current_user=current_user,
            own_permission=(
                Permission.PRODUCT_UPDATE_OWN
            ),
            all_permission=(
                Permission.PRODUCT_UPDATE_ALL
            ),
        )

        product = (
            self.product_repository
            .get_by_public_id(
                public_id=product_public_id,
                owner_id=owner_id,
            )
        )

        if product is None:
            raise NotFoundError(
                "Urun bulunamadi"
            )

        if product.id is None:
            raise RuntimeError(
                "Urun internal ID bulunamadi"
            )

        existing_detail = (
            self.detail_repository
            .get_by_product_id(
                product.id
            )
        )

        if existing_detail is None:
            raise NotFoundError(
                "Urun detayi bulunamadi"
            )

        detail = ProductDetail(
            id=existing_detail.id,
            product_id=product.id,
            description=self._normalize_text(
                description
            ),
            brand=self._normalize_text(
                brand
            ),
            warranty_months=(
                warranty_months
            ),
        )

        updated_detail = (
            self.detail_repository.update(
                detail
            )
        )

        if updated_detail is None:
            raise NotFoundError(
                "Urun detayi bulunamadi"
            )

        return updated_detail

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

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
                    "Kullanici internal ID "
                    "bulunamadi"
                )

            return current_user.id

        return None