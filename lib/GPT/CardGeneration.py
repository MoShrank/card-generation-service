from typing import Any, List, Optional

from adapters.database_models.ModelConfig import Message, Messages, ModelConfig
from adapters.database_models.Note import GPTCard
from config import env_config
from lib.GPT.GPTInterface import GPTInterface


class CardGenerationMock(GPTInterface):
    def __init__(self) -> None:
        pass

    def __call__(self, text: str, user_id: str) -> List[GPTCard]:
        return [
            GPTCard(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
            GPTCard(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
            GPTCard(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
        ]


class CardGeneration(GPTInterface):
    def __call__(self, text: str, user_id: str) -> List[GPTCard]:
        preprocessed_text = self.preprocess(text)

        messages = self._generate_messages(preprocessed_text)
        completion = self._get_completion(messages, user_id)

        cards = self.postprocess(completion)

        return cards

    def _generate_messages(self, prompt: str) -> Messages:
        system_message = self._model_config.system_message
        messages = [
            Message(role="system", content=system_message),
            Message(role="user", content=prompt),
        ]

        return messages

    def preprocess(self, text: str) -> str:
        return text.replace("\n\n", "\n")

    def postprocess(self, completion: str) -> Any:
        qas = completion.split("\n\n")

        parsed_qas = []
        for qa in qas:
            split_qa = qa.split("\n")
            if len(split_qa) == 2:
                question = split_qa[0].strip().replace("Front: ", "")
                answer = split_qa[1].strip().replace("Back: ", "")
                card = GPTCard(question=question, answer=answer)
                parsed_qas.append(card)

        return parsed_qas


card_generation: GPTInterface


def init(model_config: Optional[ModelConfig] = None) -> None:
    global card_generation

    if env_config.is_prod() and model_config:
        card_generation = CardGeneration(model_config, env_config.OPENAI_API_KEY)
    else:
        card_generation = CardGenerationMock()


def get_card_generation() -> GPTInterface:
    return card_generation
