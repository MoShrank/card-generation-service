import hashlib
from typing import Dict

from models.ModelConfig import Example, ModelConfig
from models.Note import Card


def get_qa_text(qa: Card) -> str:
    return "Q: " + qa.question + "\nA: " + qa.answer


def get_example_text(
    example: Example, stop_sequence: str, card_prefix: str, note_prefix: str
) -> str:
    examples_text = "\n".join([get_qa_text(qa) for qa in example.cards])

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


def preprocess_text(text: str) -> str:
    return text.replace("\n\n", "\n")


def generate_prompt(text: str, model_config: ModelConfig) -> str:
    preprocessed_text = preprocess_text(text)
    examples_text = "\n\n".join(
        [
            get_example_text(
                example,
                model_config.parameters.stop_sequence[0],
                model_config.card_prefix,
                model_config.note_prefix,
            )
            for example in model_config.examples
        ]
    )

    prompt = (
        model_config.prompt_prefix
        + "\n\n"
        + examples_text
        + "\n\n"
        + model_config.note_prefix
        + "\n"
        + preprocessed_text
        + "\n\n"
        + model_config.card_prefix
        + "\n"
        + "Q:"
    )

    return prompt


def encode_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
