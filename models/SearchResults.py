from pydantic import BaseModel

from models.HttpModels import BaseResponse
from text.VectorStore import SourceTypes


class ChatQuestion(BaseModel):
    query: str
    chat_history: list[str]


class SearchResult(BaseModel):
    type: SourceTypes
    ids: list[str]


class QuestionResponseData(BaseModel):
    search_results: list[SearchResult]
    answer: str


QuestionResponse = BaseResponse[QuestionResponseData]
