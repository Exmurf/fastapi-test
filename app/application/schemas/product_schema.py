from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock:int = Field(ge=0)

class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock:int = Field(ge=0)

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str
    price:float
    stock:int

class PaginatedProductResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    
