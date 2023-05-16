import openai
import tiktoken

from models.ModelConfig import Messages, ModelParameters


def calculate_chat_gpt_token_size(messages: Messages, model: str) -> int:
    """
    Calculates the number of tokens
    required to generate a GPT-based chat response for the given messages.

    Args:
        messages: A list of dictionaries representing messages in the chat conversation.
                  Each message should have a "role"
                  key with a value of either "user" or "assistant", and a "content"
                key with a value of the message text.

    Returns:
        An integer representing the number of tokens
        required to generate a response for the given messages.

    Note: This function is copied from OpenAI's documentation and
          the calculation may change in the future.
          (https://platform.openai.com/docs/guides/chat/introduction)
    """
    num_tokens = 0

    for message in messages:
        num_tokens += (
            4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        )
        for key, value in message.dict().items():
            num_tokens += get_no_tokens(value, model)
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token

    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def get_no_tokens(text: str, model: str) -> int:
    encoder = tiktoken.encoding_for_model(model)

    no_tokens = len(encoder.encode(text))

    return no_tokens


def get_chatgpt_completion(
    parameters: ModelParameters, messages: Messages, user_id: str
) -> str:
    completion = openai.ChatCompletion.create(
        model=parameters.model,
        messages=[m.dict() for m in messages],
        temperature=parameters.temperature,
        max_tokens=parameters.max_tokens,
        top_p=parameters.top_p,
        n=parameters.n,
        stop=parameters.stop_sequence,
        presence_penalty=parameters.presence_penalty,
        frequency_penalty=parameters.frequency_penalty,
        user=user_id,
    )

    return completion.choices[0].message["content"]
