import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import parse_obj_as

from database.db_interface import DBInterface
from dependencies import get_summarizer, get_web_content_repo
from models.HttpModels import EmptyResponse, HTTPException
from models.PyObjectID import PyObjectID
from models.WebContent import (
    WebContent,
    WebContentCreatedResponse,
    WebContentData,
    WebContentRequest,
    WebContentResponse,
)
from text.extract_info import extract_info
from text.Summarizer import SummarizerInterface
from util.scraper import get_content

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/post",
    tags=["web-content", "scraping"],
)


@router.get(
    "",
    response_model_by_alias=False,
    response_model=WebContentResponse,
)
async def get_posts(
    userID: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
) -> WebContentResponse:
    webContentDB = await web_content_repo.query({"user_id": userID})
    webpages = parse_obj_as(List[WebContentData], webContentDB)

    return WebContentResponse(
        data=webpages,
        message="Successfully retrieved webpages",
    )


@router.post(
    "",
    response_model_by_alias=False,
    response_model=WebContentCreatedResponse,
)
async def create_post(
    userID: str,
    body: WebContentRequest,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
    summarizer: SummarizerInterface = Depends(get_summarizer),
) -> WebContentCreatedResponse:
    url = body.url

    raw_content = get_content(url)
    if not raw_content:
        raise HTTPException(
            status_code=500,
            message="Failed to scrape web page",
            error="Failed to scrape web pag",
        )

    info = extract_info(raw_content)

    now = datetime.now()

    summary = None

    if body.summarise:
        try:
            summary = summarizer(info["content"], userID)
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                message="Failed to summarise web page",
                error="Failed to summarise web page",
            )

    web_content = WebContent(
        user_id=userID,
        url=url,
        name=body.name,
        title=info["title"],
        content=info["content"],
        summarise=body.summarise,
        created_at=now,
        updated_at=now,
        deleted_at=None,
        summary=summary,
        thumbnail=None,
    )

    result = await web_content_repo.insert_one(web_content.dict(by_alias=True))

    webContent = WebContentData(
        _id=result.inserted_id,
        url=web_content.url,
        summary=web_content.summary,
        name=web_content.name,
        created_at=web_content.created_at,
    )

    return WebContentCreatedResponse(message="succes", data=webContent)


@router.delete(
    "/{postID}",
    response_model_by_alias=False,
    response_model=EmptyResponse,
)
async def delete_post(
    userID: str,
    postID: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
) -> EmptyResponse:
    result = await web_content_repo.delete_one(
        {"_id": PyObjectID(postID), "user_id": userID}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            message="Failed to delete web page",
            error="Web page not found",
        )

    return EmptyResponse(message="succes")
