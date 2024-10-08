import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from adapters.http_models.SearchResults import (
    QuestionResponse,
    QuestionResponseData,
    SearchResult,
)
from adapters.vector_store.VectorStore import (
    ContentSourceType,
    VectorStore,
)
from lib.GPT.GPTInterface import GPTInterface
from lib.GPT.QuestionAnswerGPT import get_qa_model

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/search",
    tags=["search"],
)

INCLUDE_SOURCE_TYPES: list[ContentSourceType] = ["pdf", "url", "doi"]


def build_gpt_context(documents: list[str]) -> str:
    context = ""

    for idx, document in enumerate(documents):
        context += f"Source {idx}: {document}\n"

    return context


@router.get(
    "",
    response_model=QuestionResponse,
    response_model_by_alias=False,
)
async def search(
    userID: str,
    query: str,
    vector_store: Annotated[VectorStore, Depends()],
    qa_gpt: GPTInterface = Depends(get_qa_model),
):
    results = vector_store.query(
        query,
        {
            "user_id": userID,
            "source_type": INCLUDE_SOURCE_TYPES,
        },
    )

    query_results: dict = {key: [] for key in INCLUDE_SOURCE_TYPES}

    for idx in range(len(results["documents"])):
        metadata = results["metadatas"][idx]
        document = results["documents"][idx]

        source_type = metadata["source_type"]
        source_id = metadata["source_id"]

        if source_type in query_results:
            query_results[source_type].append(
                {
                    "id": source_id,
                    "document": document,
                }
            )

    context_docs = []

    for source_type in INCLUDE_SOURCE_TYPES:
        if len(query_results[source_type]) > 0:
            context_docs += query_results[source_type][0]["document"]

    if len(context_docs) > 0:
        answer = qa_gpt(context_docs, query, userID)
    else:
        answer = "Could not find any results in your knowledge base. Please refine your question."

    search_results: list[SearchResult] = []

    for source_type in INCLUDE_SOURCE_TYPES:
        if len(query_results[source_type]) > 0:
            search_results.append(
                SearchResult(
                    type=source_type,
                    ids=[result["id"] for result in query_results[source_type]],
                )
            )

    question_response_data = QuestionResponseData(
        search_results=search_results,
        answer=answer,
    )

    return QuestionResponse(
        message="success",
        data=question_response_data,
    )
