import hashlib
from typing import Dict

examples = {
    "text": "A neuron, also called brain cell, consists of dendrites, its input, a cell body, also called soma and axons, its output. The information in form of electrical signals, flows from the dendrites to the soma and to the axons. The soma is enclosed into a cell membrane, a bilayer of lipid molecules which act as an electric insulator. The cell membrane contains ionic channels that allow ions (negatively charged particle) to flow in and out. ",
    "qas": [
        {"question": "Q: What is a neuron?", "answer": "A brain cell"},
        {
            "question": "What does a neuron consist of?",
            "answer": "Dendrites, soma, axon",
        },
        {
            "question": "How does information flow?",
            "answer": "from dendrites to the soma to the axon",
        },
        {
            "question": "What is the soma enclosed in?",
            "answer": "A cell membrane",
        },
        {
            "question": "What is the cell membrane?",
            "answer": "A bilayer of lipid molecules",
        },
        {
            "question": "What does the cell membrane contain?",
            "answer": "Ionic channels",
        },
        {"question": "What is an ion?", "answer": "A negatively charged particle"},
    ],
}

prompt_prefix = "Generate flashcard as questions and answer from the study notes."


def get_qa_text(qa: Dict[str, str]) -> str:
    return "Q: " + qa["question"] + "\nA: " + qa["answer"]


def generate_prompt(text: str) -> str:
    # mypy: ignore-errors
    example_text: str = examples["text"]
    # mypy: ignore-errors
    qas = "\n\n".join([get_qa_text(qa) for qa in examples["qas"]])

    prompt = (
        prompt_prefix
        + "\n\n"
        + "Examples"
        + "\n\n"
        + "Study Notes:"
        + "\n"
        + example_text
        + "\n\n"
        + "Flashcards:"
        + "\n"
        + qas
        + "\n\n"
        + "Study Notes:"
        + "\n"
        + text
        + "\n\n"
        + "Flashcards:"
        + "\n"
        + "Q:"
    )

    return prompt


def encode_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
