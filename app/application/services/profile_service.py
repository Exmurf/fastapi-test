from app.application.exceptions import (
    AuthorizationError,
    NotFoundError,
)
from app.domain.entities.profile import Profile
from app.domain.entities.user import User
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.domain.security.authorization import (
    Permission,
    has_permission,
)


class ProfileService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        user_repository: UserRepository,
    ):
        self.profile_repository = profile_repository
        self.user_repository = user_repository

    def get_own_profile(
        self,
        current_user,
    ) -> dict:
        self._require_permission(
            current_user,
            Permission.PROFILE_READ_OWN,
        )

        user_id = self._get_user_id(current_user)

        profile = (
            self.profile_repository
            .get_by_user_id(user_id)
        )

        if profile is None:
            raise NotFoundError(
                "Profil bulunamadi"
            )

        return self._build_response(
            user=current_user,
            profile=profile,
        )

    def update_own_profile(
        self,
        current_user: User,
        first_name: str | None,
        last_name: str | None,
        bio: str | None,
    ) -> dict:
        self._require_permission(
            current_user,
            Permission.PROFILE_UPDATE_OWN,
        )

        return self._update_profile(
            target_user=current_user,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
        )

    def get_user_profile(
        self,
        current_user: User,
        user_public_id: str,
    ) -> dict:
        self._require_permission(
            current_user,
            Permission.PROFILE_READ_ALL,
        )

        target_user = (
            self.user_repository
            .get_by_public_id(user_public_id)
        )

        if target_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

        target_user_id = self._get_user_id(
            target_user
        )

        profile = (
            self.profile_repository
            .get_by_user_id(target_user_id)
        )

        if profile is None:
            raise NotFoundError(
                "Profil bulunamadi"
            )

        return self._build_response(
            user=target_user,
            profile=profile,
        )

    def update_user_profile(
        self,
        current_user: User,
        user_public_id: str,
        first_name: str | None,
        last_name: str | None,
        bio: str | None,
    ) -> dict:
        self._require_permission(
            current_user,
            Permission.PROFILE_UPDATE_ALL,
        )

        target_user = (
            self.user_repository
            .get_by_public_id(user_public_id)
        )

        if target_user is None:
            raise NotFoundError(
                "Kullanici bulunamadi"
            )

        return self._update_profile(
            target_user=target_user,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
        )

    def _update_profile(
        self,
        target_user: User,
        first_name: str | None,
        last_name: str | None,
        bio: str | None,
    ) -> dict:
        target_user_id = self._get_user_id(
            target_user
        )

        existing_profile = (
            self.profile_repository
            .get_by_user_id(target_user_id)
        )

        if existing_profile is None:
            raise NotFoundError(
                "Profil bulunamadi"
            )

        profile = Profile(
            id=existing_profile.id,
            user_id=target_user_id,
            first_name=self._normalize_text(
                first_name
            ),
            last_name=self._normalize_text(
                last_name
            ),
            bio=self._normalize_text(bio),
        )

        updated_profile = (
            self.profile_repository.update(
                profile
            )
        )

        if updated_profile is None:
            raise NotFoundError(
                "Profil guncellenemedi"
            )

        return self._build_response(
            user=target_user,
            profile=updated_profile,
        )

    @staticmethod
    def _require_permission(
        user: User,
        permission: Permission
    ) -> None:
        if not has_permission(
            user.role,
            permission,
        ):
            raise AuthorizationError(
                "Bu islem icin yetkiniz yok"
            )

    @staticmethod
    def _get_user_id(
        user: User,
    ) -> int:
        if user.id is None:
            raise RuntimeError(
                "Kullanicinin internal ID "
                "degeri bulunamadi"
            )

        return user.id

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        return normalized_value


    @staticmethod
    def _build_response(
        user: User,
        profile: Profile,
    ) -> dict:
        if user.public_id is None:
            raise RuntimeError(
                "Kullanicinin public ID "
                "degeri bulunamadi"
            )

        return {
            "user": {
                "public_id": user.public_id,
                "email": user.email,
            },
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "bio": profile.bio,
        }


