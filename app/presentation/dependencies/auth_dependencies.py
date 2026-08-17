from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.application.exceptions import (
    AuthenticationError,
)
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.application.security.password_hasher import (
    PasswordHasher,
)
from app.config import settings
from app.domain.entities.user import User
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from app.infrastructure.security.argon2_password_hasher import(
    Argon2PasswordHasher,
)
from app.infrastructure.security.jwt_access_token_service import (
    JWTAccessTokenService,
)
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.application.security.refresh_token_service import (
    RefreshTokenService,
)
from app.infrastructure.repositories.sqlalchemy_refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.security.opaque_refresh_token_service import (
    OpaqueRefreshTokenService,
)
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)
from app.infrastructure.repositories.sqlalchemy_profile_repository import (
    SQLAlchemyProfileRepository,
)


password_hasher = Argon2PasswordHasher()

access_token_service = JWTAccessTokenService(
    secret_key=(
        settings.jwt_secret_key.get_secret_value()
    ),
    algorithm=settings.jwt_algorithm,
    expire_minutes=(
        settings.access_token_expire_minutes
    ),
)

bearer_scheme = HTTPBearer(
    auto_error=False
)

refresh_token_service = OpaqueRefreshTokenService(
    expire_days=settings.refresh_token_expire_days
)

def get_user_repository(
        db: Session = Depends(get_db),
) -> UserRepository:
    return SQLAlchemyUserRepository(db)

def get_password_hasher() -> PasswordHasher:
    return password_hasher

def get_access_token_service() -> AccessTokenService:
    return access_token_service

def get_profile_repository(
        db: Session = Depends(get_db),
) -> ProfileRepository:
    return SQLAlchemyProfileRepository(db)

def get_current_user(
        credentials: (
            HTTPAuthorizationCredentials | None
        ) = Depends(bearer_scheme),
        token_service: AccessTokenService = Depends(
            get_access_token_service
        ),
        user_repository: UserRepository = Depends(
            get_user_repository
        ),
) -> User:
    if credentials is None:
        raise AuthenticationError(
            "Kimlik dogrulama gerekli"
        )

    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError(
            "Gecersiz kimlik dogrulama yontemi"
        )

    token_payload = (
        token_service.decode_access_token(
            credentials.credentials
        )
    )

    if token_payload is None:
        raise AuthenticationError(
            "Gecersiz veya suresi dolmus access token"
        )

    user = user_repository.get_by_public_id(
        token_payload.subject
    )

    if (
        user is None
        or not user.is_active
        or user.is_deleted
    ):
        raise AuthenticationError(
            "Gecersiz veya suresi dolmus access token"
        )

    return user

def get_refresh_token_repository(
        db: Session = Depends(get_db),
) -> RefreshTokenRepository:
    return SQLAlchemyRefreshTokenRepository(db)

def get_refresh_token_service() -> RefreshTokenService:
    return refresh_token_service
