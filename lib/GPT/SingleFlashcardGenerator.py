from typing import Optional

from config import env_config
from adapters.database_models.ModelConfig import (
    GPTCard,
    Message,
    Messages,
    ModelConfig,
)
from lib.GPT.GPTInterface import GPTInterface


class SingleFlashcardGeneratorMock(GPTInterface):
    def __init__(self) -> None:
        pass

    def __call__(self, text: str, user_id: str) -> GPTCard:
        return GPTCard(
            question="What is the capital of the United States?",
            answer="Washington D.C.",
        )

    def _generate_messages(self) -> Messages:
        return []


class SingleFlashcardGenerator(GPTInterface):

    def __call__(self, text: str, user_id: str) -> GPTCard:
        messages = self._generate_messages(text)
        completion = self._get_completion(messages, user_id)
        card = self._postprocess(completion)

        return card

    def _postprocess(self, completion: str) -> GPTCard:
        split_completion = completion.split("\n")

        question = split_completion[0].replace("Q: ", "")
        answer = split_completion[1].replace("A: ", "")

        card = GPTCard(question=question, answer=answer)

        return card

    def _generate_messages(self, text: str) -> Messages:
        system_message = self._model_config.system_message
        messages = [
            Message(role="system", content=system_message),
            Message(role="user", content=text),
        ]

        return messages


single_card_generator: GPTInterface


def init(model_config: Optional[ModelConfig] = None) -> None:
    global single_card_generator

    if env_config.is_prod() and model_config:
        single_card_generator = SingleFlashcardGenerator(
            model_config=model_config,
            openai_api_key=env_config.OPENAI_API_KEY,
        )
    else:
        single_card_generator = SingleFlashcardGeneratorMock()


def get_single_card_generator() -> GPTInterface:
    return single_card_generator
