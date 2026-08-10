from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.infrastructure.database import Base, engine
from app.infrastructure.models.product_model import ProductModel
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.models.refresh_token_model import RefreshTokenModel
from app.infrastructure.models.profile_model import ProfileModel
from app.presentation.routers.product_router import router as product_router
from app.presentation.routers.auth_router import(
    router as auth_router,
)
from app.presentation.routers.profile_router import (
    router as profile_router
)
from app.presentation.routers.analytics_router import (
    router as analytics_router,
)
from app.application.exceptions import (
    NotFoundError, 
    ValidationError,
    ConflictError,
    AuthenticationError,
    AuthorizationError,
)
from app.infrastructure.models.tag_model import TagModel
from app.infrastructure.models.product_tag_model import product_tags
from app.infrastructure.models.product_detail_model import ProductDetailModel
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title= settings.app_name,
    debug = settings.debug,
)

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(
    request: Request,
    error: AuthenticationError,
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status": False,
            "data": {},
            "message": str(error),
            "errors": None,
        },
        headers={
            "WWW-Authenticate": "Bearer",
        }
    )

@app.exception_handler(AuthorizationError)
async def authorization_error_handler(
    request: Request,
    exc: AuthorizationError,
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "status": False,
            "data": {},
            "message": str(exc),
            "errors": None,
        },
        headers={
            "WWW-Authenticate": "Bearer",
        }
    )

@app.exception_handler(ConflictError)
async def conflict_error_handler(
    request: Request,
    error: ConflictError,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": False,
            "data": {},
            "message": str(error),
            "errors": None,
        },
    )

@app.exception_handler(NotFoundError)
def not_found_exception_handler(
    request: Request,
    error: NotFoundError,
):
    return JSONResponse(
        status_code= status.HTTP_404_NOT_FOUND,
        content={
            "status": False,
            "data": {},
            "message": str(error),
        },
    )

@app.exception_handler(ValidationError)
def validation_exception_handler(
    request: Request,
    error: ValidationError,
):
    return JSONResponse(
        status_code= status.HTTP_400_BAD_REQUEST,
        content={
            "status": False,
            "data": {},
            "message": str(error),
        },
    )

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    error: RequestValidationError,
):
    formatted_errors = []

    for validation_error in error.errors():
        location = validation_error["loc"]

        field_parts = [
            str(part)
            for part in location
            if part not in {"body", "query", "path"}
        ]

        formatted_errors.append(
            {
                "field": ".".join(field_parts),
                "message": validation_error["msg"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status": False,
            "data": {},
            "message": "Gonderilen veriler gecersiz",
            "errors": formatted_errors,
        }
    )

app.include_router(product_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {"message": "Product API calisiyor"}