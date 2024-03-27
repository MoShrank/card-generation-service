import io
import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import parse_obj_as

from database.db_interface import DBInterface
from dependencies import (
    Collections,
    get_pdf_storage,
    get_pdf_to_md,
    get_repo,
    get_vector_store,
)
from models.HttpModels import EmptyResponse, HTTPException
from models.PDF import (
    PDFModel,
    PDFPostRes,
    PDFPostResData,
    PDFResData,
    PDFResponse,
    PDFSearchResponse,
    PDFSearchResponseData,
    ProcessingStatus,
)
from models.PyObjectID import PyObjectID
from text.PDFStorage import PDFStorageInterface
from text.SciPDFToMD import SciPDFToMDInterface
from text.VectorStore import VectorStoreInterface

logger = logging.getLogger(__name__)

repo = get_repo(Collections.PDF.value)

router = APIRouter(
    prefix="/pdf",
    tags=["pdf-content", "content-extraction"],
)


async def pdf_to_markdown(
    id: str,
    user_id: str,
    pdf: bytes,
    repo: DBInterface,
    pdf_to_md: SciPDFToMDInterface,
    vector_store: VectorStoreInterface,
    pdf_storage: PDFStorageInterface,
):
    markdown = None
    status = "failed"

    storage_reference = pdf_storage.upload_pdf(user_id, id, io.BytesIO(pdf))

    try:
        markdown = await run_in_threadpool(lambda: pdf_to_md(pdf))
        status = "processed"
    except Exception as e:
        logger.error(f"Failed to convert pdf to markdown: {e}")

    if markdown:
        vector_store.add_document(
            markdown,
            {
                "source_type": "pdf",
                "source_id": id,
                "user_id": user_id,
            },
        )

    obj_id = PyObjectID(id)

    await repo.update_one(
        {"_id": obj_id, "user_id": user_id},
        {
            "$set": {
                "extracted_markdown": markdown,
                "processing_status": status,
                "updated_at": datetime.now(),
                "storage_reference": storage_reference,
            },
        },
    )


@router.get(
    "",
    response_model=PDFResponse,
    response_model_by_alias=False,
)
async def get_pdf(
    userID: str,
    pdf_repo: DBInterface = Depends(repo),
) -> PDFResponse:
    pdfs = await pdf_repo.query({"user_id": userID})

    parsed_pdfs = parse_obj_as(list[PDFResData], pdfs)

    return PDFResponse(
        data=parsed_pdfs,
        message="Successfully retrieved pdfs",
    )


@router.post(
    "",
    response_model=PDFPostRes,
    response_model_by_alias=False,
)
async def create_pdf(
    background_tasks: BackgroundTasks,
    userID: str,
    file: UploadFile = File(...),
    pdf_repo: DBInterface = Depends(repo),
    pdf_to_md: SciPDFToMDInterface = Depends(get_pdf_to_md),
    vector_store: VectorStoreInterface = Depends(get_vector_store),
    pdf_storage: PDFStorageInterface = Depends(get_pdf_storage),
):
    pdf_file_content = await file.read()

    now = datetime.now()
    status: ProcessingStatus = "processing"

    try:
        pdf = PDFModel(
            user_id=userID,
            processing_status=status,
            created_at=now,
            updated_at=now,
            title=None,
            storage_ref=None,
            extracted_markdown=None,
            summary=None,
            deleted_at=None,
        )

    except Exception as e:
        logger.error(f"Failed to create pdf: {e}")
        raise HTTPException(
            status_code=400,
            message="Failed to create pdf",
            error="Failed to create pdf",
        )

    try:
        result = await pdf_repo.insert_one(pdf.dict(by_alias=True))
        pdf_id = result.inserted_id
    except Exception as e:
        logger.error(f"Failed to save pdf to database: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to create pdf",
            error="Failed to save pdf to database",
        )

    background_tasks.add_task(
        pdf_to_markdown,
        str(pdf_id),
        userID,
        pdf_file_content,
        pdf_repo,
        pdf_to_md,
        vector_store,
        pdf_storage,
    )

    return PDFPostRes(
        message="Successfully created pdf",
        data=PDFPostResData(
            id=str(pdf_id),
            processing_status=status,
        ),
    )


@router.delete("/{pdf_id}")
async def delete_pdf(
    userID: str,
    pdf_id: str,
    pdf_repo: DBInterface = Depends(repo),
) -> EmptyResponse:
    obj_id = PyObjectID(pdf_id)

    await pdf_repo.delete_one({"_id": obj_id, "user_id": userID})

    return EmptyResponse(message="Successfully deleted pdf")


@router.get("/{pdf_id}/search")
async def search_pdf(
    userID: str,
    pdf_id: str,
    query: str,
    pdf_repo: DBInterface = Depends(repo),
    vector_store: VectorStoreInterface = Depends(get_vector_store),
) -> PDFSearchResponse:
    pdf = await pdf_repo.find_by_id(pdf_id, {"user_id": userID})

    if not pdf:
        raise HTTPException(
            status_code=404,
            message="Failed to find pdf",
            error="PDF not found",
        )

    if pdf["processing_status"] == "processing":
        raise HTTPException(
            status_code=400,
            message="Failed to search pdf",
            error="PDF is still processing",
        )

    filter = {
        "user_id": userID,
        "source_id": pdf_id,
    }
    query_results = vector_store.query(query, filter)["documents"]

    markdown: str = pdf["extracted_markdown"]
    data = []

    for answer in query_results:
        start_idx = markdown.find(answer)
        end_idx = start_idx + len(answer)

        data.append(
            PDFSearchResponseData(
                answer=answer,
                start_idx=start_idx,
                end_idx=end_idx,
            )
        )

    return PDFSearchResponse(message="success", data=data)
