from abc import ABC, abstractmethod
from typing import Any

import openai

from external.gpt import get_chatgpt_completion
from adapters.database_models.ModelConfig import Messages, ModelConfig
from util.error import retry_on_exception


class GPTInterface(ABC):
    _model_config: ModelConfig

    def __init__(self, model_config: ModelConfig, openai_api_key: str) -> None:
        self._model_config = model_config
        openai.api_key = openai_api_key

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    @retry_on_exception(Exception, max_retries=3, sleep_time=5)
    def _get_completion(
        self,
        messages: Messages,
        user_id: str,
    ) -> str:
        completion = get_chatgpt_completion(
            self._model_config.parameters, messages, user_id
        )

        return completion
