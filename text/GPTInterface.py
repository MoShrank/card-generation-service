from abc import ABC, abstractmethod

from external.gpt import get_chatgpt_completion
from models.ModelConfig import Messages, ModelConfig
from util.error import retry_on_exception


class GPTInterface(ABC):
    _model_config: ModelConfig

    @abstractmethod
    def _generate_messages(self, *args, **kwargs) -> Messages:
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
