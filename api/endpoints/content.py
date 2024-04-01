import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile

from adapters.database_models.PyObjectID import PyObjectID
from adapters.http_models.Content import CreateContentData, CreateContentRequest
from adapters.http_models.HttpModels import BaseResponse, EmptyResponse, HTTPException
from adapters.PDFStorage import PDFStorage
from adapters.repository import ContentRepository
from usecases import CreateContentUsecase

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/content",
    tags=["content"],
)


@router.post("", response_model=BaseResponse[CreateContentData])
async def create_content(
    userID: str,
    create_content_usecase: Annotated[CreateContentUsecase, Depends()],
    request: Request,
    file: Optional[UploadFile] = File(None),
):
    content_source = None

    if file:
        if file.filename.endswith(".pdf") and file.content_type == "application/pdf":
            content_source = await file.read()
        else:
            raise HTTPException(
                status_code=400,
                message="Only PDF files are supported",
                error="Invalid file type",
            )
    else:
        try:
            body = await request.json()
            content_source = CreateContentRequest(**body).source
        except:  # noqa E722
            raise HTTPException(
                status_code=400,
                message="Please provide a valid content type",
                error="No valid content provided",
            )

    try:
        content_obj = await create_content_usecase(content_source, userID)
    except Exception as e:
        logger.error(f"Failed to create content: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to create content",
            error="Internal Server Error",
        )

    res_data = content_obj.dict(by_alias=False)
    res_data["id"] = str(res_data["id"])

    return BaseResponse(message="success", data=CreateContentData(**res_data))


@router.get("", response_model=BaseResponse[list[CreateContentData]])
async def get_content(
    userID: str,
    content_repository: Annotated[ContentRepository, Depends()],
    ids: Optional[list[str]] = Query(None),
):
    query = {"user_id": userID}
    if ids:
        ids = [PyObjectID(id) for id in ids]
        query["_id"] = {"$in": ids}

    try:
        content = await content_repository.query(query)
    except Exception as e:
        logger.error(f"Failed to get content: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to get content",
            error="Internal Server Error",
        )

    res_data = [CreateContentData(**c) for c in content]

    return BaseResponse(message="success", data=res_data)


@router.delete("/{id}")
async def delete_pdf(
    userID: str,
    id: str,
    content_repository: Annotated[ContentRepository, Depends()],
) -> EmptyResponse:
    is_deleted = await content_repository.delete_one({"id": id, "user_id": userID})

    if not is_deleted:
        message = "Failed to delete content"
    else:
        message = "Successfully deleted content"

    return EmptyResponse(message=message)


@router.get("/file/{id}")
async def download_pdf(
    userID: str,
    id: str,
    pdf_storage: Annotated[PDFStorage, Depends()],
):
    try:
        pdf = pdf_storage.download_pdf(userID, id)
    except Exception as e:
        logger.error(f"Failed to download PDF. Error: {e}")
        raise HTTPException(
            status_code=404,
            message="Failed to download PDF",
            error="PDF not found",
        )

    pdf = pdf.read()

    return Response(content=pdf, media_type="application/pdf")


# TODO
# search_content / qa
