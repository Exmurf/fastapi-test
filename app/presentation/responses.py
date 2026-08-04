from typing import Any, Generic, Literal, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    status: Literal[True] = True
    data: T

class ApiErrorResponse(BaseModel):
    status: Literal[False] = False
    data: dict = Field(default_factory=dict)
    message: str
    errors: list[dict[str, Any]] | None = None

def success_response(data: T) -> dict:
    return{
        "status": True,
        "data": data,
    }