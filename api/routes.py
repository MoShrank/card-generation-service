from fastapi import APIRouter

from api.endpoints.notes import router as notes_router
from api.endpoints.pdf import router as pdf_router
from api.endpoints.search import router as search_router
from api.endpoints.web_content import router as web_content_router

routers = APIRouter()
router_list = [notes_router, pdf_router, search_router, web_content_router]

for router in router_list:
    routers.include_router(router)
