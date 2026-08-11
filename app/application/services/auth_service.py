from app.application.exceptions import (
    ConflictError,
    AuthenticationError,
)
from app.application.security.password_hasher import (
    PasswordHasher,
)
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.domain.entities.user import User
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.application.security.refresh_token_service import (
    RefreshTokenService,
)
from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.domain.security.authorization import UserRole
from app.domain.entities.profile import Profile
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)
from app.application.services.activity_log_service import ActivityLogService
from app.domain.activity_log_types import (
    ActivityAction,
    ActivityEntityType,
)


from datetime import datetime, timezone

class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        profile_repository: ProfileRepository,
        password_hasher: PasswordHasher,
        access_token_service: AccessTokenService,
        refresh_token_repository: RefreshTokenRepository,
        refresh_token_service: RefreshTokenService,
        activity_log_service: ActivityLogService,
    ):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
        self.password_hasher = password_hasher
        self.access_token_service = access_token_service
        self.refresh_token_repository = refresh_token_repository
        self.refresh_token_service = refresh_token_service
        self.activity_log_service = activity_log_service

    def register(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = (
            self.user_repository.get_by_email(
                normalized_email
            )
        )

        if existing_user is not None:
            raise ConflictError(
                "Bu e-posta adresi zaten kayitli"
            )

        password_hash = self.password_hasher.hash(
            password
        )

        user = User(
            id=None,
            public_id=None,
            email=normalized_email,
            password_hash=password_hash,
            role=UserRole.USER,
            is_active=True,
        )

        created_user = self.user_repository.create(user)

        if created_user.id is None:
            raise RuntimeError(
                "Olusturulan kullanicinin internal ID degeri bulunamadi"
            )

        profile = Profile(
            id=None,
            user_id=created_user.id,
            first_name=None,
            last_name=None,
            bio=None,
        )

        self.profile_repository.create(profile)

        self.activity_log_service.log(
            user=created_user,
            action=ActivityAction.USER_REGISTER,
            entity_type=ActivityEntityType.USER,
            entity_id=created_user.public_id,
            old_value=None,
            new_value=None,
        )

        return created_user

    def login(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        user = self.user_repository.get_by_email(
            normalized_email
        )

        if user is None:
            raise AuthenticationError(
                "E-posta veya sifre hatali"
            )

        password_is_valid = self.password_hasher.verify(
            plain_password=password,
            password_hash=user.password_hash,
        )

        if not password_is_valid:
            raise AuthenticationError(
                "E-posta veya sifre hatali"
            )

        if not user.is_active:
            raise AuthenticationError(
                "E-posta veya sifre hatali"
            )

        if user.public_id is None:
            raise RuntimeError(
                "Kullanicinin public_id degeri bulunamadi"
            )

        access_token = (
            self.access_token_service.create_access_token(
                subject=user.public_id
            )
        )

        if user.id is None:
            raise RuntimeError(
                "Kullanicinin internal id degeri bulunamadi"
            )

        generated_refresh_token = (
            self.refresh_token_service.generate_refresh_token()
        )

        refresh_token = RefreshToken(
            id = None,
            user_id = user.id,
            token_hash = generated_refresh_token.token_hash,
            expires_at = generated_refresh_token.expires_at,
            created_at = datetime.now(timezone.utc),
            revoked_at = None,
        )

        self.refresh_token_repository.create(
            refresh_token
        )

        self.activity_log_service.log(
            user=user,
            action=ActivityAction.AUTH_LOGIN,
            entity_type=ActivityEntityType.USER,
            entity_id=user.public_id,
            old_value=None,
            new_value=None,
        )

        return {
            "access_token": access_token,
            "refresh_token": generated_refresh_token.raw_token,
            "token_type": "bearer",
            "expires_in": (
                self.access_token_service
                .expires_in_seconds
            ),
            "user": user,
        }

    def refresh_access_token(
        self,
        raw_refresh_token: str,
    ) -> dict:
        token_hash = (
            self.refresh_token_service.hash_token(
                raw_refresh_token
            )
        )

        stored_refresh_token = (
            self.refresh_token_repository
            .get_by_token_hash(token_hash)
        )

        if stored_refresh_token is None:
            raise AuthenticationError(
                "Gecersiz veya suresi dolmus refresh token"
            )

        if stored_refresh_token.revoked_at is not None:
            raise AuthenticationError(
                "Gecersiz veya suresi dolmus refresh token"
            )

        now = datetime.now(timezone.utc)

        expires_at = stored_refresh_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo = timezone.utc
            )

        if expires_at <= now:
            raise AuthenticationError(
                "Gecersiz veya suresi dolmus refresh token"
            )

        user = self.user_repository.get_by_id(
            stored_refresh_token.user_id
        )

        if(
            user is None
            or not user.is_active
            or user.id is None
            or user.public_id is None
        ):
            raise AuthenticationError(
                "Gecersiz veya suresi dolmus refresh token"
            )

        revoked = (
            self.refresh_token_repository.revoke(
                token_hash
            )
        )

        if not revoked:
            raise AuthenticationError(
                "Gecersiz veya suresi dolmus refresh token"
            )

        generated_refresh_token = (
            self.refresh_token_service
            .generate_refresh_token()
        )

        new_refresh_token = RefreshToken(
            id = None,
            user_id = user.id,
            token_hash = (
                generated_refresh_token.token_hash
            ),
            expires_at = (
                generated_refresh_token.expires_at
            ),
            created_at = now,
            revoked_at = None,
        )

        self.refresh_token_repository.create(
            new_refresh_token
        )

        access_token = (
            self.access_token_service
            .create_access_token(
                subject = user.public_id
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": (
                generated_refresh_token.raw_token
            ),
            "token_type": "bearer",
            "expires_in": (
                self.access_token_service
                .expires_in_seconds
            ),
        }

    def logout(
        self,
        raw_refresh_token: str,
    ) -> bool:
        token_hash = (
            self.refresh_token_service.hash_token(
                raw_refresh_token
            )
        )

        refresh_token = (
            self.refresh_token_repository
            .get_by_token_hash(token_hash)
        )

        if refresh_token is None:
            raise AuthenticationError(
                "Gecersiz refresh token"
            )

        if refresh_token.revoked_at is not None:
            raise AuthenticationError(
                "Refresh token zaten iptal edilmis"
            )

        user = self.user_repository.get_by_id(
            refresh_token.user_id
        )

        if (
            user is None
            or user.id is None
            or user.public_id is None
        ):
            raise AuthenticationError(
                "Kullanici bulunamadi"
            )

        revoked = (
            self.refresh_token_repository.revoke(
                token_hash
            )
        )

        if not revoked:
            raise AuthenticationError(
                "Refresh token iptal edilemedi"
            )

        self.activity_log_service.log(
            user=user,
            action=ActivityAction.AUTH_LOGOUT,
            entity_type=ActivityEntityType.USER,
            entity_id=user.public_id,
            old_value=None,
            new_value=None,
        )

        return True