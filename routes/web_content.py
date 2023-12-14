import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import parse_obj_as

from database.db_interface import DBInterface
from dependencies import (
    get_question_answer_gpt,
    get_summarizer,
    get_vector_store,
    get_web_content_repo,
)
from models.HttpModels import EmptyResponse, HTTPException
from models.PyObjectID import PyObjectID
from models.WebContent import (
    WebContent,
    WebContentCreatedResponse,
    WebContentQA,
    WebContentQAResponse,
    WebContentRequest,
    WebContentResponse,
    WebContentResponseData,
)
from text.content.ContentExtractor import ContentExtractor
from text.QuestionAnswerGPT import QuestionAnswerGPTInterface
from text.Summarizer import SummarizerInterface
from text.VectorStore import VectorStoreInterface

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/post",
    tags=["web-content", "scraping"],
)


@router.get(
    "",
    response_model=WebContentResponse,
    response_model_by_alias=False,
)
async def get_posts(
    userID: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
) -> WebContentResponse:
    webContentDB = await web_content_repo.query({"user_id": userID})

    webpages = parse_obj_as(list[WebContentResponseData], webContentDB)

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
    vector_store: VectorStoreInterface = Depends(get_vector_store),
) -> WebContentCreatedResponse:
    src = body.url

    content_extractor = ContentExtractor()

    try:
        content = content_extractor(src)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            message="Failed to get Content. If you want to get a webpage, make sure that you add http at the beginning.",
            error=str(e),
        )

    now = datetime.now()

    text = content.content
    title = content.title

    try:
        summary = summarizer(text, userID)
    except Exception as e:
        logger.error(f"Failed to summarise webpage. Error: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to summarise web page",
            error="Failed to summarise web page",
        )

    raw_content = content.raw_content

    web_content = WebContent(
        user_id=userID,
        url=src,
        name=title,
        title=title,
        html=raw_content,
        content=text,
        created_at=now,
        updated_at=now,
        deleted_at=None,
        summary=summary,
    )

    result = await web_content_repo.insert_one(web_content.dict(by_alias=True))

    result_id = str(result.inserted_id)

    webContent = WebContentResponseData(
        id=result_id,
        url=web_content.url,
        summary=web_content.summary,
        name=web_content.name,
        created_at=web_content.created_at,
    )

    vector_store.add_document(
        text, {"user_id": userID, "source_id": str(result.inserted_id)}
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


@router.get(
    "/{postID}/answer",
    response_model=WebContentQAResponse,
)
async def get_answer(
    userID: str,
    postID: str,
    question: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
    vector_store: VectorStoreInterface = Depends(get_vector_store),
    qa_gpt: QuestionAnswerGPTInterface = Depends(get_question_answer_gpt),
) -> WebContentQAResponse:
    web_content = await web_content_repo.find_one(
        {"_id": PyObjectID(postID), "user_id": userID}
    )

    if not web_content:
        raise HTTPException(
            status_code=404,
            message="Failed to get answer",
            error="Web page not found",
        )

    filter = {
        "user_id": userID,
        "source_id": postID,
    }

    documents = vector_store.query(web_content["content"], filter)["documents"]

    if not documents:
        raise HTTPException(
            status_code=404,
            message="Failed to get answer",
            error="No documents found",
        )

    answer = qa_gpt(documents, question, userID)

    return WebContentQAResponse(
        message="success",
        data=WebContentQA(
            answer=answer,
            documents=documents,
        ),
    )


@router.get(
    "/search",
    response_model=WebContentResponse,
    response_model_by_alias=False,
)
async def search_posts(
    userID: str,
    query: str,
    web_content_repo: DBInterface = Depends(get_web_content_repo),
    vector_store: VectorStoreInterface = Depends(get_vector_store),
) -> WebContentResponse:
    filter = {
        "user_id": userID,
    }

    metadatas = vector_store.query(query, filter)["metadatas"]

    articles = []

    if metadatas and len(metadatas) > 0:
        ids = [PyObjectID(doc["source_id"]) for doc in metadatas]
        webContentDB = await web_content_repo.query(
            {"_id": {"$in": ids}, "user_id": userID}
        )
        articles = parse_obj_as(list[WebContentResponseData], webContentDB)

    return WebContentResponse(
        data=articles,
        message="Successfully retrieved webpages",
    )
