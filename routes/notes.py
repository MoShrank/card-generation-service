from datetime import datetime
from typing import List

import openai
from config import env_config
from database.db_interface import DBInterface
from dependencies import get_db
from fastapi import APIRouter, Depends, Request
from models.HttpModels import ErrorResponse
from models.MongoModel import MongoModel
from models.Note import Card, Cards, CardsResponse, Note, NotesResponse
from models.PyObjectID import PyObjectId
from pydantic import BaseModel, Field
from text_processing.post_processing import parse_completion
from text_processing.pre_processing import encode_text, generate_prompt
from util import limiter

USER_RATE_LIMIT = env_config.USER_RATE_LIMIT_PER_MINUTE

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


class Text(BaseModel):
    text: str
    deck_id: str


def make_openai_request(prompt: str, user_id: str):
    res = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150,
        temperature=0.5,
        top_p=1,
        n=1,
        user=user_id,
    )

    return res


class CardGenerationModel(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    deck_id: str
    input_text: str
    completion: str
    cards: List[Card]
    cards_added: bool
    original_cards: bool
    created_at: str


def get_latest_cards_from_note(note: Note) -> List[Card]:
    cards = sorted(note["cards"], key=lambda x: x["created_at"])[0]["cards"]

    return cards


@router.post("")
@limiter.limit(f"{USER_RATE_LIMIT}/minute")
async def generate_cards(
    request: Request,
    Text: Text,
    userID: str,
    db: DBInterface = Depends(get_db),
):
    text = Text.text
    hash = encode_text(text)

    note = await db.find_one({"encoding": hash})
    if note:
        cards = get_latest_cards_from_note(note)
        return CardsResponse(
            message="Note already exists", data={**note, "cards": cards}
        )

    prompt = generate_prompt(text=Text.text)
    response = make_openai_request(prompt=prompt, user_id=userID)
    completion = response.choices[0].text
    parsed_qas = parse_completion(completion=completion)

    cards = Cards(
        cards=parsed_qas,
        cards_added=False,
        original_cards=True,
        created_at=datetime.now().isoformat(),
    )

    document = Note(
        encoding=hash,
        user_id=userID,
        deck_id=Text.deck_id,
        text=Text.text,
        completion=completion,
        cards_added=False,
        cards=[cards],
        created_at=datetime.now().isoformat(),
    ).dict()

    await db.insert_one(document)

    return CardsResponse(message="success", data={**document, "cards": cards.cards})


"""
@router.post("/cards")
async def add_cards():
    pass



@router.put("/{id}")
async def update_cards(
    id: str,
    request: Request,
    cards: List[Card],
    user_id: str,
    deck_id: str,
    db: DBInterface = Depends(get_db),
):
    note = await db.find_one({"_id": id, "user_id": user_id, "deck_id": deck_id})
    if not note:
        return ErrorResponse(message="No note found", error="No note found")

    cards = Cards(
        cards=cards,
        cards_added=False,
        original_cards=False,
        created_at=datetime.now().isoformat(),
    )

    document = CardGenerationModel(
        **Cards.dict(),
    ).dict()
    await db.update_one(id=id, document=document)

    return GeneratedCardsResponse(message="Successfully updated cards", data=document)
"""


@router.get("")
async def get_note(request: Request, userID: str, db: DBInterface = Depends(get_db)):
    notes = list(await db.query({"user_id": userID, "cards_added": False}))

    if not notes:
        return ErrorResponse(message="No cards found", error="No cards found")

    notes_by_deck = {}
    for note in notes:
        deck_id = note["deck_id"]
        cards = get_latest_cards_from_note(note)

        notes_by_deck[deck_id] = {**note, "cards": cards}

    return NotesResponse(message="success", data=notes_by_deck)
