import hashlib


def generate_prompt(text: str) -> str:
    prompt = (
        "Generate a list of 6 questions and answers from the text provided below."
        "\n"
        "###"
        "Text:"
        f"{text}"
        "###"
        "\n"
        "List of 6 questions and answers:"
        "Q:"
    )

    return prompt


def encode_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
