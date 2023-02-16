import logging
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends

from database.db_interface import DBInterface
from dependencies import get_web_content_repo
from models import WebContent
from models.HttpModels import HTTPException
from models.WebContent import WebContentRequest, WebContentResponse
from text_processing.extract_info import extract_info
from util.scraper import get_content

logger = logging.getLogger("logger")


router = APIRouter(
    prefix="/web-content",
    tags=["web-content", "scraping"],
)


@router.get("/post")
async def get_posts(
    userID: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
) -> WebContentResponse:
    webpages: List[Dict] = await web_content_repo.query({"user_id": userID})

    return WebContentResponse(
        data=webpages,
        message="Successfully retrieved webpages",
    )


@router.post("/post")
async def create_post(
    userID: str,
    body: WebContentRequest,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
) -> WebContentResponse:
    url = body.url

    raw_content = get_content(url)
    if not raw_content:
        raise HTTPException(
            status_code=500,
            message="Failed to scrape web page",
            error="Failed sending request to deck service",
        )

    info = extract_info(raw_content)

    web_content = WebContent.WebContent(
        user_id=userID,
        url=url,
        title=info["title"],
        content=info["content"],
        summarise=body.summarise,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    if body.summarise:
        web_content.summary = "TODO"

    await web_content_repo.insert_one(web_content.dict(by_alias=True))

    return WebContentResponse(url=web_content.url, summary=web_content.summarise)
