from fastapi import(
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.application.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    UserResponse,
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
    ApiErrorResponse,
    success_response,
)
from app.config import settings
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.infrastructure.security.jwt_access_token_service import (
    JWTAccessTokenService,
)
from app.presentation.dependencies.auth_dependencies import (
    get_access_token_service,
    get_current_user,
    get_password_hasher,
    get_user_repository,
    get_profile_repository,
)
from app.domain.entities.user import User
from app.application.security.refresh_token_service import (
    RefreshTokenService,
)
from app.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.presentation.dependencies.auth_dependencies import (
    get_refresh_token_repository,
    get_refresh_token_service,
)
from app.domain.repositories.profile_repository import (
    ProfileRepository,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def get_auth_service(
        user_repository: UserRepository = Depends(
            get_user_repository
        ),
        profile_repository: ProfileRepository = Depends(
            get_profile_repository
        ),
        password_hasher: PasswordHasher = Depends(
            get_password_hasher
        ),
        access_token_service: AccessTokenService = Depends(
            get_access_token_service
        ),
        refresh_token_repository: RefreshTokenRepository = Depends(
            get_refresh_token_repository
        ),
        refresh_token_service: RefreshTokenService = Depends(
            get_refresh_token_service
        ),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        profile_repository=profile_repository,
        password_hasher=password_hasher,
        access_token_service=access_token_service,
        refresh_token_repository=refresh_token_repository,
        refresh_token_service=refresh_token_service,
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

@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return success_response(current_user)

@router.post(
    "/refresh",
    response_model = ApiResponse[RefreshTokenResponse],
    responses = {
        401: {"model": ApiErrorResponse},
    },
)
def refresh_access_token(
    request: RefreshTokenRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    result = service.refresh_access_token(
        raw_refresh_token=(
            request.refresh_token
        )
    )

    return success_response(result)

@router.post(
    "/logout",
    response_model = ApiResponse[dict],
    status_code = status.HTTP_200_OK,
    responses = {
        401: {"model": ApiErrorResponse},
    },
)
def logout(
    request: LogoutRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):
    service.logout(
        raw_refresh_token=request.refresh_token
    )

    return success_response(
        {
            "message": (
                "Basariyla cikis yapildi"
            ),
        }
    )