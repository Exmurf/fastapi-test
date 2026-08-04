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


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        access_token_service: AccessTokenService,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.access_token_service = (
            access_token_service
        )

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
            is_active=True,
        )

        return self.user_repository.create(user)

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

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": (
                self.access_token_service
                .expires_in_seconds
            ),
            "user": user,
        }