import os
import re
from typing import Tuple

from transformers import pipeline

MODEL_PATH = os.environ.get("MODEL_PATH", "./qa_model")


class CardSourceGeneratorMock:
    def __call__(self, text: str, question: str) -> Tuple[int, int]:
        return 0, len(text) // 2


class CardSourceGenerator:
    def __init__(self) -> None:
        self._qa_model = pipeline(
            "question-answering", model=MODEL_PATH, tokenizer=MODEL_PATH
        )

    def __call__(self, text: str, question: str) -> Tuple[int, int]:
        answer = self._qa_model(question=question, context=text)

        start, end = self._find_sentence_indices(text, answer["start"], answer["end"])
        return start, end

    def _find_sentence_indices(
        self, text: str, substring_start: int, substring_end: int
    ) -> Tuple[int, int]:
        """
        Finds the starting and ending indices of the sentence that contains the substring.
        """
        sentences = re.split(r"\n|(?<=[.!?])\s+", text)
        substring = text[substring_start:substring_end]

        for sentence in sentences:
            index = sentence.lower().find(substring.lower())
            if index != -1:
                start = text.index(sentence)
                end = start + len(sentence)
                return start, end

        return substring_start, substring_end
