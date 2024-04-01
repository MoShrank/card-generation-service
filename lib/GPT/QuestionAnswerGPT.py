from config import env_config
from lib.gpt import get_chatgpt_completion
from adapters.database_models.ModelConfig import Message, ModelConfig
from lib.GPT.GPTInterface import GPTInterface


class QuestionAnswerGPT(GPTInterface):
    def __call__(self, documents: list[str], question: str, user_id: str) -> str:
        text = "\n\n".join(documents)

        system_prompt = self._model_config.system_message.format(question=question)

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=text),
        ]

        completion = get_chatgpt_completion(
            self._model_config.parameters, messages, user_id
        )

        return completion


qa_model: GPTInterface


def init(model_config: ModelConfig) -> None:
    global qa_model
    qa_model = QuestionAnswerGPT(model_config, env_config.OPENAI_API_KEY)


def get_qa_model() -> GPTInterface:
    return qa_model
