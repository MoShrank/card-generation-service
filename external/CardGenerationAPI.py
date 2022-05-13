from abc import ABC, abstractmethod
from typing import Any, Union

import openai
from config import EnvConfig
from models.ModelConfig import ModelConfig, ModelParameters
from util.AttrDict import AttrDict


class CardGenerationAPIInterface(ABC):
    @abstractmethod
    def generate_cards(self, prompt: str, user_id: str) -> str:
        pass

    @abstractmethod
    def set_config(self, config: ModelConfig) -> None:
        pass


class CardGenerationAPI(CardGenerationAPIInterface):
    _model_parameters: ModelParameters

    def __init__(
        self,
        config: EnvConfig,
    ):
        openai.api_key = config.OPENAI_API_KEY

    def set_config(self, model_config: ModelConfig):
        self._model_parameters = model_config.parameters

    def generate_cards(self, prompt: str, user_id: str) -> str:
        res = openai.Completion.create(
            temperature=self._model_parameters.temperature,
            engine=self._model_parameters.engine,
            max_tokens=self._model_parameters.max_tokens,
            top_p=self._model_parameters.top_p,
            n=self._model_parameters.n,
            stop=self._model_parameters.stop_sequence,
            prompt=prompt,
            user=user_id,
        )

        return res


class CardGenerationAPIMock(CardGenerationAPIInterface):
    def set_config(self, model_config: ModelConfig):
        pass

    def generate_cards(self, prompt: str, user_id: str) -> Any:
        text = AttrDict()
        text.update(
            {
                "text": """Q: What is the capital of the United States? A: Washington D.C. Q: What is the capital of the United States? A: Washington D.C. Q: What is the capital of the United States? A: Washington D.C. Q: What is the capital of the United States? A: Washington D.C. Q: What is the capital of the United States? A: Washington D.C.""",
            }
        )

        response = AttrDict()
        response.update({"choices": [text]})

        return response
