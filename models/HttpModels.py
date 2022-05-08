from abc import ABC
from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel, ABC):
    message: str
    data: Any


class ErrorResponse(BaseModel):
    message: str
    error: str
