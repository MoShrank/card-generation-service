from abc import ABC, abstractmethod
from typing import Literal, NotRequired, Optional, TypedDict, cast
from uuid import uuid4

from chromadb.api import ClientAPI
from chromadb.utils import embedding_functions

from text.chroma_client import chroma_client
from text.TextSplitter import TextSplitterInterface

COLLECTION_NAME = "content"

SourceTypes = Literal["pdf", "web"]

Include = list[
    Literal["documents", "embeddings", "metadatas", "distances", "uris", "data"]
]


class QueryFilters(TypedDict):
    source_id: NotRequired[str]
    source_types: list[SourceTypes] | SourceTypes
    user_id: str


class MetaData(TypedDict):
    source_id: str
    source_type: SourceTypes
    user_id: str


class QueryResult(TypedDict):
    ids: list[str]
    documents: list[str]
    metadatas: list[MetaData]
    distances: list[float]


SearchQueryOperators = Literal["$and", "$or"]
SearchQuery = dict[SearchQueryOperators, list[dict[str, str]]]

# TODO: cutoff for number of results + relevance score -> only return results above a certain distance


class VectorStoreInterface(ABC):
    @abstractmethod
    def add_document(self, document: str, metadata: MetaData):
        pass

    @abstractmethod
    def add_documents(self, documents: list[str], metadatas: list[MetaData]):
        pass

    @abstractmethod
    def query(
        self,
        query: str,
        filter_values: QueryFilters,
    ) -> QueryResult:
        pass


class VectorStore(VectorStoreInterface):
    def __init__(
        self,
        document_splitter: TextSplitterInterface,
        chroma_client: ClientAPI = chroma_client,
        max_query_results: int = 5,
    ):
        default_ef = embedding_functions.DefaultEmbeddingFunction()

        self._collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=default_ef  # type: ignore
        )

        self._max_query_results = max_query_results
        self._chunk_char_size = 1000
        self._overlap = 100
        self._document_splitter = document_splitter

    def add_document(self, document: str, metadata: MetaData):
        split_documents = self._document_splitter(document)

        ids = [self._generate_id() for _ in split_documents]

        metadatas = [metadata for _ in split_documents]

        self._collection.add(
            documents=split_documents,
            ids=ids,
            metadatas=metadatas,  # type: ignore
        )

    def add_documents(self, documents: list[str], metadatas: list[MetaData]):
        for document, metadata in zip(documents, metadatas):
            self.add_document(document, metadata)

    def _compose_and_filter(self, filter_values: dict[str, str]) -> Optional[dict]:
        if not filter_values:
            return None

        if len(filter_values) == 1:
            return filter_values

        filter: SearchQuery = {"$and": []}

        for key, value in filter_values.items():
            if isinstance(value, list):
                filter["$and"].append({key: {"$in": value}})
            elif value:
                filter["$and"].append({key: value})

        return filter

    def query(
        self,
        query: str,
        filter_values: QueryFilters,
    ) -> QueryResult:
        query_filter = self._compose_and_filter(cast(dict[str, str], filter_values))

        results = self._collection.query(
            query_texts=[query],
            n_results=self._max_query_results,
            where=query_filter,
            include=["documents", "metadatas", "distances"],
        )

        return {
            "ids": results["ids"][0],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],  # type: ignore
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def _generate_id(self) -> str:
        return str(uuid4())
