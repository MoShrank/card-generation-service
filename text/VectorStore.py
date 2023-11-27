from abc import ABC, abstractmethod
from typing import Literal, Mapping, Optional, Union
from uuid import uuid4

import chromadb  # type: ignore
from chromadb.utils import embedding_functions  # type: ignore

from text.chroma_client import chroma_client
from text.TextSplitter import TextSplitterInterface

COLLECTION_NAME = "webContent"

Metadata = Mapping[str, Union[str, int, float]]

Include = list[
    Union[
        Literal["documents"],
        Literal["embeddings"],
        Literal["metadatas"],
        Literal["distances"],
    ]
]

SearchQueryOperators = Literal["$and", "$or"]
SearchQuery = dict[SearchQueryOperators, list[dict[str, str]]]

# TODO: cutoff for number of results + relevance score -> only return results above a certain distance


class VectorStoreInterface(ABC):
    @abstractmethod
    def add_document(self, document: str, metadata: Optional[Metadata] = None):
        pass

    @abstractmethod
    def add_documents(self, documents: list[str], metadatas: list[Metadata]):
        pass

    @abstractmethod
    def query(
        self,
        query: str,
        filter_values: dict[str, str],
        include: Include = ["documents"],
    ) -> dict:
        pass


class VectorStore(VectorStoreInterface):
    def __init__(
        self,
        document_splitter: TextSplitterInterface,
        chroma_client: chromadb.Client = chroma_client,
        max_query_results: int = 5,
    ):
        default_ef = embedding_functions.DefaultEmbeddingFunction()

        self._collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=default_ef
        )

        self._max_query_results = max_query_results
        self._chunk_char_size = 1000
        self._overlap = 100
        self._document_splitter = document_splitter

    def add_document(self, document: str, metadata: Optional[Metadata] = None):
        split_documents = self._document_splitter(document)

        ids = [self._generate_id() for _ in split_documents]

        metadatas = [metadata for _ in split_documents] if metadata else None

        self._collection.add(
            documents=split_documents,
            ids=ids,
            metadatas=metadatas,
        )

    def add_documents(self, documents: list[str], metadatas: list[Metadata]):
        for document, metadata in zip(documents, metadatas):
            self.add_document(document, metadata)

    def _compose_and_filter(self, filter_values: dict[str, str]) -> Optional[dict]:
        if not filter_values:
            return None

        if len(filter_values) == 1:
            return filter_values

        filter: SearchQuery = {"$and": []}

        for key, value in filter_values.items():
            filter["$and"].append({key: value})

        return filter

    def query(
        self,
        query: str,
        filter_values: dict[str, str],
        include: Include = ["documents"],
    ) -> dict:
        query_filter = self._compose_and_filter(filter_values)

        results = self._collection.query(
            query_texts=[query],
            n_results=self._max_query_results,
            where=query_filter,
            include=include,
        )

        return results

    def _generate_id(self) -> str:
        return str(uuid4())
