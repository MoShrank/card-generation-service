import logging
from typing import Annotated, Any, Optional, Union

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile

from adapters.database_models.PyObjectID import PyObjectID
from adapters.http_models.Content import (
    ContentData,
    CreateContentRequest,
    UpdateAnnotationsRequest,
    UpdateContentData,
)
from adapters.http_models.HttpModels import BaseResponse, EmptyResponse, HTTPException
from adapters.PDFStorage import PDFStorage
from adapters.repository import ContentRepository
from usecases import CreateContentUsecase

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/content",
    tags=["content"],
)


@router.post("", response_model=BaseResponse[ContentData])
async def create_content(
    userID: str,
    create_content_usecase: Annotated[CreateContentUsecase, Depends()],
    request: Request,
    file: Optional[UploadFile] = File(None),
):
    content_source: Optional[Union[str, bytes]] = None

    if file:
        if (
            file.filename
            and file.filename.endswith(".pdf")
            and file.content_type == "application/pdf"
        ):
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
        except:  # noqa
            raise HTTPException(
                status_code=400,
                message="Please provide a valid content type",
                error="No valid content provided",
            )

    try:
        content_obj = await create_content_usecase(content_source, userID)
    except:  # noqa
        raise HTTPException(
            status_code=500,
            message="Failed to create content",
            error="Internal Server Error",
        )

    res_data = content_obj.dict(by_alias=False)
    res_data["id"] = str(res_data["id"])

    return BaseResponse(message="success", data=ContentData(**res_data))


@router.put("/{id}/annotation")
async def update_annotations(
    userID: str,
    id: str,
    body: UpdateAnnotationsRequest,
    content_repository: Annotated[ContentRepository, Depends()],
):
    is_updated = await content_repository.update_one(
        {"id": id, "user_id": userID},
        {"$set": body.dict()},
    )

    if not is_updated:
        message = "Failed to update annotations"
    else:
        message = "Successfully updated annotations"

    return EmptyResponse(message=message)


@router.patch("/{id}")
async def update_content(
    userID: str,
    id: str,
    body: UpdateContentData,
    content_repository: Annotated[ContentRepository, Depends()],
):
    try:
        updated_content = await content_repository.update_one(
            {"id": id, "user_id": userID}, {"$set": body.dict()}
        )
    except:  # noqa
        raise HTTPException(
            status_code=500,
            message="Failed to update content",
            error="Internal Server Error",
        )

    if not updated_content:
        return EmptyResponse(status_code=400, message="Failed to update content")

    else:
        return EmptyResponse(status_code=200, message="Successfully updated content")


@router.get("", response_model=BaseResponse[list[ContentData]])
async def get_content(
    userID: str,
    content_repository: Annotated[ContentRepository, Depends()],
    ids: Optional[list[str]] = Query(None),
):
    query: dict[str, Any] = {"user_id": userID}
    if ids:
        query["_id"] = {"$in": [PyObjectID(id) for id in ids]}

    try:
        content = await content_repository.query(query)
    except:  # noqa
        raise HTTPException(
            status_code=500,
            message="Failed to get content",
            error="Internal Server Error",
        )

    res_data = [ContentData(**c) for c in content]

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

    return Response(content=pdf.read(), media_type="application/pdf")


# TODO
# search_content / qa
