import re
from typing import Tuple

from transformers import pipeline


class CardSourceGenerator:
    def __init__(self) -> None:
        self._qa_model = pipeline("question-answering")

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
        start = substring_start
        end = substring_end

        substring = text[substring_start:substring_end]
        sentence_pattern = r"(?<=[.?!]\s)(.*?{}.*?)\s*[.?!]".format(
            re.escape(substring)
        )

        # Find the starting index of the sentence that contains the substring
        match = re.search(sentence_pattern, text)
        if match:
            start = match.start()

        end_match = re.search(sentence_pattern, text[start:])
        if end_match:
            end = end_match.start()

        return start, end + 1
