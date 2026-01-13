from pydantic import BaseModel, Generic, TypeVar
from typing import Optional, Any

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None
