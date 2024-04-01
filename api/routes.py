from fastapi import APIRouter

from api.endpoints.content import router as content_router
from api.endpoints.notes import router as notes_router

routers = APIRouter()
router_list = [
    notes_router,
    content_router,
]

for router in router_list:
    routers.include_router(router)
