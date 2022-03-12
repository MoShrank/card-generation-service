import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Text(BaseModel):
    text: str


def init():
    load_dotenv("./.env")


init()


def generate_propmpt(text: str):
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


def make_openai_request(prompt: str):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    res = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150,
        temperature=0.5,
        top_p=1,
        n=1,
    )

    return res.choices[0].text


def parse_response(response: str):
    response = "Q: " + response
    qas = response.split("Q:")

    parsed_qas = []
    for qa in qas:
        qa = qa.split("A:")
        if len(qa) == 2:
            parsed_qas.append({"question": qa[0].strip(), "answer": qa[1].strip()})

    return parsed_qas


@app.get("/ping")
async def ping():
    return {"ping": "pong!"}


@app.post("/cards")
async def generate_cards(Text: Text):
    prompt = generate_propmpt(text=Text.text)
    response = make_openai_request(prompt=prompt)
    print(response)
    parsed_qas = parse_response(response=response)

    return {"cards": parsed_qas, "completion": response}
