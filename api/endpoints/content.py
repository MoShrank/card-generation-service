import logging

from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/content",
    tags=["content"],
)
