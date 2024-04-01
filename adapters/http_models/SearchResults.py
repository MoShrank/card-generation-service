from pydantic import BaseModel

from adapters.http_models.HttpModels import BaseResponse
from adapters.vector_store.VectorStore import ContentSourceType


class ChatQuestion(BaseModel):
    query: str
    chat_history: list[str]


class SearchResult(BaseModel):
    type: ContentSourceType
    ids: list[str]


class QuestionResponseData(BaseModel):
    search_results: list[SearchResult]
    answer: str


QuestionResponse = BaseResponse[QuestionResponseData]
