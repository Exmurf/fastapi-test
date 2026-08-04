from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.infrastructure.database import Base, engine
from app.infrastructure.models.product_model import ProductModel
from app.presentation.routers.product_router import router as product_router
from app.application.exceptions import NotFoundError, ValidationError
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title= settings.app_name,
    debug = settings.debug,
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

@app.get("/")
def root():
    return {"message": "Product API calisiyor"}