from fastapi import FastAPI

from app.infrastructure.database import Base, engine
from app.infrastructure.models.product_model import ProductModel
from app.presentation.routers.product_router import router as product_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product API")
app.include_router(product_router)

@app.get("/")
def root():
    return {"message": "Product API calisiyor"}