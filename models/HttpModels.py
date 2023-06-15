from abc import ABC
from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel, ABC):
    message: str
    data: Any


class EmptyResponse(BaseModel):
    message: str


class HTTPException(Exception):
    def __init__(self, status_code: int, message: str, error: str):
        self.status_code = status_code
        self.message = message
        self.error = error
