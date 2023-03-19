import time
from abc import ABC, abstractmethod
from typing import Any, List

import openai

from models.ModelConfig import Example, ModelConfig
from models.Note import Card


def retry_on_exception(exception, max_retries=3, sleep_time=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception:
                    retries += 1
                    if retries == max_retries:
                        raise
                time.sleep(sleep_time)

        return wrapper

    return decorator


class CardGenerationInterface(ABC):
    @abstractmethod
    def __call__(self, text: str, user_id: str) -> List[Card]:
        pass


class CardGenerationMock(CardGenerationInterface):
    def __call__(self, text: str, user_id: str) -> List[Card]:
        return [
            Card(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
            Card(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
            Card(
                question="What is the capital of the United States?",
                answer="Washington D.C.",
            ),
        ]


class CardGeneration(CardGenerationInterface):
    _model_config: ModelConfig

    def __init__(self, model_config: ModelConfig, openai_api_key: str) -> None:
        openai.api_key = openai_api_key
        self._model_config = model_config

    def __call__(self, text: str, user_id: str) -> List[Card]:
        preprocessed_text = self.preprocess(text)
        prompt = self._generate_prompt(preprocessed_text)
        completion = self._generate_cards(prompt, user_id)
        cards = self.postprocess(completion)

        return cards

    def preprocess(self, text: str) -> str:
        return text.replace("\n\n", "\n")

    def postprocess(self, completion: str) -> Any:
        print(completion)
        qas = completion.split("\n\n")

        parsed_qas = []
        for qa in qas:
            split_qa = qa.split("\n")
            if len(split_qa) == 2:
                question = split_qa[0].strip().replace("Q: ", "")
                answer = split_qa[1].strip().replace("A: ", "")
                card = Card(question=question, answer=answer)
                parsed_qas.append(card)

        return parsed_qas

    @retry_on_exception(exception=openai.error.APIConnectionError)
    def _generate_cards(self, prompt: str, user_id: str) -> str:
        completion = openai.ChatCompletion.create(
            model=self._model_config.parameters.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self._model_config.parameters.temperature,
            max_tokens=self._model_config.parameters.max_tokens,
            top_p=self._model_config.parameters.top_p,
            n=self._model_config.parameters.n,
            stop=self._model_config.parameters.stop_sequence,
            user=user_id,
        )

        return completion.choices[0].message["content"]

    def _get_qa_text(self, qa: Card) -> str:
        return "Q: " + qa.question + "\nA: " + qa.answer

    def _get_example_text(
        self, example: Example, stop_sequence: str, card_prefix: str, note_prefix: str
    ) -> str:
        examples_text = "\n\n".join([self._get_qa_text(qa) for qa in example.cards])

        example_text = (
            note_prefix
            + "\n"
            + example.note
            + "\n"
            + card_prefix
            + "\n"
            + examples_text
            + "\n\n"
            + stop_sequence
        )

        return example_text

    def _generate_prompt(self, text: str) -> str:
        examples_text = ""

        if len(self._model_config.examples):
            examples_text = "\n\n".join(
                [
                    self._get_example_text(
                        example,
                        self._model_config.parameters.stop_sequence[0],
                        self._model_config.card_prefix,
                        self._model_config.note_prefix,
                    )
                    for example in self._model_config.examples
                ]
            )

            examples_text += "\n\n" + self._model_config.parameters.stop_sequence[0]

        prompt = (
            self._model_config.prompt_prefix
            + "\n\n"
            + examples_text
            + self._model_config.note_prefix
            + "\n"
            + text
            + "\n\n"
            + self._model_config.card_prefix
            + "\n"
        )

        return prompt
