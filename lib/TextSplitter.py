from abc import ABC, abstractmethod


class TextSplitterInterface(ABC):
    @abstractmethod
    def __call__(self, text: str) -> list[str]:
        pass


class TextSplitter(TextSplitterInterface):
    def __init__(self, chunk_char_size: int, overlap: int):
        self._chunk_char_size = chunk_char_size
        self._overlap = overlap

    def __call__(
        self,
        text: str,
    ) -> list[str]:
        chunks = self._split(text)

        return chunks

    def _split(self, text: str) -> list[str]:
        chunks = []
        start = 0
        end = self._chunk_char_size

        while start < len(text):
            chunk = text[start:end]
            chunks.append(chunk)

            start += self._chunk_char_size - self._overlap
            end = start + self._chunk_char_size

        return chunks
