from external.gpt import get_chatgpt_completion
from models.ModelConfig import Message
from text.GPT.GPTInterface import GPTInterface


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
