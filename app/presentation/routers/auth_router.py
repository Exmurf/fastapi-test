from fastapi import(
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.application.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    LoginResponse,
)
from app.application.security.password_hasher import(
    PasswordHasher,
)
from app.application.services.auth_service import (
    AuthService,
)
from app.domain.repositories.user_repository import (
    UserRepository,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_user_repository import(
    SQLAlchemyUserRepository,
)
from app.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from app.presentation.responses import (
    ApiResponse,
    success_response,
)
from app.config import settings
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.infrastructure.security.jwt_access_token_service import (
    JWTAccessTokenService,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

argon2_password_hasher = Argon2PasswordHasher()

jwt_access_token_service = JWTAccessTokenService(
    secret_key=(
        settings.jwt_secret_key.get_secret_value()
    ),
    algorithm=settings.jwt_algorithm,
    expire_minutes=(
        settings.access_token_expire_minutes
    ),
)

def get_access_token_service(
) -> AccessTokenService:
    return jwt_access_token_service

def get_user_repository(
        db: Session = Depends(get_db),
) -> UserRepository:
    return SQLAlchemyUserRepository(db)

def get_password_hasher() -> PasswordHasher:
    return argon2_password_hasher

def get_auth_service(
        user_repository: UserRepository = Depends(
            get_user_repository
        ),
        password_hasher: PasswordHasher = Depends(
            get_password_hasher
        ),
        access_token_service: AccessTokenService = Depends(
            get_access_token_service
        ),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        password_hasher=password_hasher,
        access_token_service=access_token_service,
    )


@router.post(
    "/register",
    status_code= status.HTTP_201_CREATED,
    response_model=ApiResponse[UserResponse],
)
def register(
    request: RegisterRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    user = service.register(
        email=str(request.email),
        password=request.password,
    )

    return success_response(user)

@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
)
def login(
    request: LoginRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    result = service.login(
        email=str(request.email),
        password=request.password,
    )

    return success_response(result)