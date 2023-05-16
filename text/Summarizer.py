from abc import ABC, abstractmethod
from typing import List

import nltk
import openai

from external.gpt import (
    calculate_chat_gpt_token_size,
    get_chatgpt_completion,
    get_no_tokens,
)
from models.ModelConfig import Message, Messages, SummarizerConfig
from util.error import retry_on_exception


class SummarizerInterface(ABC):
    @abstractmethod
    def __call__(self, text: str, user_id: str) -> str:
        pass


class SummarizerMock(SummarizerInterface):
    def __call__(self, text: str, user_id: str) -> str:
        return "Mock Summary"


class Summarizer(SummarizerInterface):
    _model_config: SummarizerConfig

    def __init__(self, config: SummarizerConfig, openai_api_key: str) -> None:
        self._model_config = config

        openai.api_key = openai_api_key

    def __call__(self, text: str, user_id: str) -> str:
        target_size = self._get_target_size()

        chunks = self._chunk_text(text, target_size)

        summaries = []

        for chunk in chunks:
            chunk_summary = self._get_completion(chunk, user_id)
            summaries.append(chunk_summary)

        summary = "\n".join(summaries)

        return summary

    def _get_target_size(self) -> int:
        messages = self._generate_messages("")
        prompt_size = calculate_chat_gpt_token_size(
            messages, self._model_config.parameters.model
        )
        completion_size = self._model_config.parameters.max_tokens

        max_model_tokens = self._model_config.max_model_tokens

        max_text_size = (
            max_model_tokens - prompt_size - completion_size - 20
        )  # 20 as a small buffer

        assert max_text_size > 100, "The maximum text size must be greater than 100."

        return max_text_size

    def _generate_messages(self, text: str) -> Messages:
        system_message = Message(
            role="system", content=self._model_config.system_message
        )
        user_message = Message(
            role="user", content=self._model_config.user_message_prefix + text
        )

        messages = [system_message, user_message]

        return messages

    @retry_on_exception(Exception, max_retries=3, sleep_time=5)
    def _get_completion(self, text: str, user_id: str) -> str:
        messages = self._generate_messages(text)

        completion = get_chatgpt_completion(
            self._model_config.parameters, messages, user_id
        )

        return completion

    def _chunk_text(self, text: str, target_size: int) -> List[str]:
        """
        Splits the given text into chunks of sentences based on the target size.

        Args:
            text (str): The text to be chunked.
            target_size (int): The maximum token size for each chunk.

        Returns:
            List[str]: A list of chunks where each chunk is a string containing sentences.

        """

        # Split the text into sentences
        sentences = nltk.sent_tokenize(text)

        chunks = []
        chunk = ""
        for sentence in sentences:
            # Calculate sentence token size to ensure it's less than the target size
            # and avoid an infinite loop
            sentence_token_size = get_no_tokens(
                sentence, self._model_config.parameters.model
            )

            assert sentence_token_size < target_size, (
                "The sentence token size is greater than the target size. "
                "Please increase the target size."
            )

            # Calculate the token size of the current chunk with the next sentence added
            new_chunk_size = get_no_tokens(
                chunk + " " + sentence, self._model_config.parameters.model
            )

            # If the new chunk size is larger than the target size, then start a new chunk
            if new_chunk_size > target_size:
                chunks.append(chunk)
                chunk = sentence
            else:
                # Add the sentence to the current chunk
                chunk += " " + sentence

        # Add the last chunk if it's not empty
        if chunk:
            chunks.append(chunk)

        return chunks
