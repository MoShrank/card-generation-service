import io
import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import parse_obj_as

from database.db_interface import DBInterface
from dependencies import Collections, get_pdf_to_md, get_repo, get_vector_store
from models.PDF import (
    PDFModel,
    PDFPostRes,
    PDFPostResData,
    PDFResData,
    PDFResponse,
    PDFSearchResponse,
    PDFSearchResponseData,
)
from models.PyObjectID import PyObjectID
from text import SciPDFToMD
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
    pdf: io.BytesIO,
    repo: DBInterface,
    pdf_to_md: SciPDFToMD,
    vector_store: VectorStoreInterface,
) -> str:
    markdown = None
    status = "failed"

    try:
        markdown = await run_in_threadpool(lambda: pdf_to_md(pdf))
        status = "processed"
    except Exception as e:
        logger.error(f"Failed to convert pdf to markdown: {e}")

    if markdown:
        metadata = {
            "source_id": id,
            "user_id": user_id,
        }

        vector_store.add_document(markdown, metadata)

    obj_id = PyObjectID(id)

    await repo.update_one(
        {"_id": obj_id, "user_id": user_id},
        {
            "$set": {
                "extracted_markdown": markdown,
                "processing_status": status,
                "updated_at": datetime.now(),
            },
        },
    )


@router.get("/", response_model=PDFResponse)
async def get_pdf(
    userID: str,
    pdf_repo: DBInterface = Depends(repo),
) -> PDFResponse:
    pdfs = await pdf_repo.query({"user_id": userID})

    pdfs = parse_obj_as(list[PDFResData], pdfs)

    return PDFResponse(
        data=pdfs,
        message="Successfully retrieved pdfs",
    )


@router.post("", response_model=PDFPostRes)
async def create_pdf(
    background_tasks: BackgroundTasks,
    userID: str,
    file: UploadFile = File(...),
    pdf_repo: DBInterface = Depends(repo),
    pdf_to_md: SciPDFToMD = Depends(get_pdf_to_md),
    vector_store: VectorStoreInterface = Depends(get_vector_store),
):
    pdf_file_content = await file.read()

    now = datetime.now()
    status = "processing"

    pdf = PDFModel(
        user_id=userID,
        pdf=pdf_file_content,
        processing_status=status,
        created_at=now,
        updated_at=now,
    )

    result = await pdf_repo.insert_one(pdf.dict(by_alias=True))
    pdf_id = result.inserted_id

    background_tasks.add_task(
        pdf_to_markdown,
        str(pdf_id),
        userID,
        pdf_file_content,
        pdf_repo,
        pdf_to_md,
        vector_store,
    )

    return PDFPostRes(
        message="Successfully created pdf",
        data=PDFPostResData(
            _id=pdf_id,
            status=status,
        ),
    )


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
    query_results = vector_store.query(query, filter)["documents"][0]

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
