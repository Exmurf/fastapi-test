from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.infrastructure.database import Base, engine
from app.infrastructure.models.product_model import ProductModel
from app.presentation.routers.product_router import router as product_router
from app.application.exceptions import NotFoundError, ValidationError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product API")

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

app.include_router(product_router)

@app.get("/")
def root():
    return {"message": "Product API calisiyor"}