from datetime import datetime

from app.application.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from app.domain.entities.user import User
from app.domain.repositories.analytics_repository import (
    AnalyticsRepository,
)
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.domain.security.authorization import (
    Permission,
    has_permission,
)


class AnalyticsService:
    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        user_repository: UserRepository,
    ):
        self.analytics_repository = (
            analytics_repository
        )
        self.user_repository = (
            user_repository
        )

    def get_own_analytics(
        self,
        current_user: User,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> dict:

        if not has_permission(
            current_user.role,
            Permission.ANALYTICS_READ_OWN,
        ):
            raise AuthorizationError(
                "Bu islem icin yetkiniz yok"
            )

        return self._get_analytics(
            target_user=current_user,
            start_date=start_date,
            end_date=end_date,
        )

    def get_user_analytics(
        self,
        current_user: User,
        user_public_id: str,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> dict:

        if not has_permission(
            current_user.role,
            Permission.ANALYTICS_READ_ALL,
        ):
            raise AuthorizationError(
                "Bu islem icin yetkiniz yok"
            )

        target_user = (
            self.user_repository
            .get_by_public_id(
                user_public_id
            )
        )

        if target_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

        return self._get_analytics(
            target_user=target_user,
            start_date=start_date,
            end_date=end_date,
        )

    def _get_analytics(
        self,
        target_user: User,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> dict:

        if target_user.id is None:
            raise RuntimeError(
                "Kullanici internal ID "
                "bulunamadi"
            )

        if target_user.public_id is None:
            raise RuntimeError(
                "Kullanici public ID "
                "bulunamadi"
            )

        if target_user.created_at is None:
            raise RuntimeError(
                "Kullanici kayit tarihi "
                "bulunamadi"
            )

        if (
            start_date is not None
            and start_date < target_user.created_at
        ):
            raise ValidationError(
                "Baslangic tarihi kullanicinin "
                "kayit tarihinden once olamaz"
            )

        if (
            end_date is not None
            and end_date < target_user.created_at
        ):
            raise ValidationError(
                "Bitis tarihi kullanicinin "
                "kayit tarihinden once olamaz"
            )

        effective_start = (
            start_date
            if start_date is not None
            else target_user.created_at
        )

        effective_end = (
            end_date
            if end_date is not None
            else datetime.now()
        )

        self._validate_date_range(
            effective_start,
            effective_end,
        )

        analytics = (
            self.analytics_repository
            .get_user_analytics(
                user_id=target_user.id,
                start_date=effective_start,
                end_date=effective_end,
            )
        )

        duration_seconds = (
            effective_end
            - effective_start
        ).total_seconds()

        duration_days = (
            duration_seconds / 86400
        )

        effective_duration_days = max(
            duration_days,
            1.0,
        )

        average_products_per_day = (
            analytics.total_products
            / effective_duration_days
        )

        return {
            "user_public_id": (
                target_user.public_id
            ),
            "email": target_user.email,
            "registered_at": (
                target_user.created_at
            ),
            "first_product_created_at": (
                analytics
                .first_product_created_at
            ),
            "total_products": (
                analytics.total_products
            ),
            "total_tags": (
                analytics.total_tags
            ),
            "average_products_per_day": round(
                average_products_per_day,
                1,
            ),
            "start_date": effective_start,
            "end_date": effective_end,
        }

    @staticmethod
    def _validate_date_range(
        start_date: datetime,
        end_date: datetime,
    ) -> None:

        if (
            start_date.tzinfo is not None
            or end_date.tzinfo is not None
        ):
            raise ValidationError(
                "Tarihler timezone "
                "icermemelidir"
            )

        if start_date >= end_date:
            raise ValidationError(
                "Baslangic tarihi bitis "
                "tarihinden once olmalidir"
            )

        if end_date > datetime.now():
            raise ValidationError(
                "Bitis tarihi gelecekte "
                "olamaz"
            )