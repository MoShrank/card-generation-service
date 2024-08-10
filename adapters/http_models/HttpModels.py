from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class BaseResponse(BaseModel, Generic[DataT]):
    message: str
    data: DataT


class EmptyResponse(BaseModel):
    status_code: int = 200
    message: str


class HTTPException(Exception):
    def __init__(self, status_code: int, message: str, error: str):
        self.status_code = status_code
        self.message = message
        self.error = error
