import logging
from datetime import datetime
from io import BytesIO
from typing import Annotated, Union

from fastapi import Depends
from fastapi.concurrency import run_in_threadpool

from adapters import PDFStorage, TaskQueue
from adapters.database_models.Content import ContentModel
from adapters.repository import ContentRepository
from adapters.vector_store.VectorStore import VectorStore, VectorStoreInterface
from lib.content import ContentExtractor
from lib.GPT.Summarizer import SummarizerInterface, get_summarizer

logger = logging.getLogger(__name__)


class CreateContentUsecase:
    _file_storage: PDFStorage
    _vector_store: VectorStoreInterface
    _repository: ContentRepository
    _content_extractor: ContentExtractor
    _task_queue: TaskQueue
    _summarizer: SummarizerInterface

    def __init__(
        self,
        repository: Annotated[ContentRepository, Depends()],
        vector_store: Annotated[VectorStore, Depends()],
        task_queue: Annotated[TaskQueue, Depends()],
        content_extractor: Annotated[ContentExtractor, Depends()],
        pdf_storage: Annotated[PDFStorage, Depends()],
        summarizer: Annotated[SummarizerInterface, Depends(get_summarizer)],
    ):
        self._repository = repository
        self._vector_store = vector_store
        self._task_queue = task_queue
        self._content_extractor = content_extractor
        self._file_storage = pdf_storage
        self._summarizer = summarizer

    async def __call__(self, source: Union[str, bytes], user_id: str):
        content_type = self._content_extractor.get_type_from_src(source)

        content_obj = ContentModel(
            user_id=user_id,
            source_type=content_type,
        )

        content_id = await self._repository.insert_one(content_obj.dict(by_alias=True))

        self._task_queue(self._process_content, content_id, user_id, source)

        return content_obj

    async def _process_content(
        self, content_id: str, user_id: str, source: Union[str, bytes]
    ):
        try:
            extracted_content = await run_in_threadpool(
                lambda: self._content_extractor(source)
            )

            storage_ref = None

            if "pdf" in extracted_content and extracted_content["pdf"]:
                storage_ref = self._file_storage.upload_pdf(
                    user_id, content_id, BytesIO(extracted_content["pdf"])
                )
                # TODO source as a keyword for different things in different
                # structures is confusion and should be improved
                # this is also just a workaround and improving the content data model
                # to also include the doi as a link would be better
                del extracted_content["pdf"]  # type: ignore

            summary = self._summarizer(extracted_content["view_text"], user_id)

            self._vector_store.add_document(
                extracted_content["view_text"],
                {
                    "source_type": extracted_content["source_type"],
                    "source_id": content_id,
                    "user_id": user_id,
                },
            )
            await self._repository.update_one(
                {"_id": content_id},
                {
                    "$set": {
                        **extracted_content,
                        "storage_ref": storage_ref,
                        "summary": summary,
                        "processing_status": "processed",
                        "updated_at": datetime.now(),
                    }
                },
            )
        except Exception as e:
            logger.error(f"Failed to process content: {e}")
            await self._repository.update_one(
                {"_id": content_id},
                {
                    "$set": {
                        "processing_status": "failed",
                        "updated_at": datetime.now(),
                    }
                },
            )
