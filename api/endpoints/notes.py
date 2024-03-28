import logging
from datetime import datetime
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, Request

from config import env_config
from database.db_interface import DBInterface
from dependencies import (
    get_card_source_generator,
    get_deck_service,
    get_note_repo,
    get_user_repo,
)
from external.DeckServiceAPI import DeckServiceAPIInterface
from models.HttpModels import HTTPException
from models.Note import (
    AddedCardsResponse,
    AddedCardsResponseData,
    Card,
    CardResponse,
    CardResponseData,
    CardsResponse,
    CardsResponseData,
    GenerateCardRequest,
    GenerateCardsRequest,
    GPTCard,
    Note,
    NotesResponse,
    NotesResponseData,
    UpdateCardsRequest,
    UpdatedCardsResponse,
    UpdatedCardsResponseData,
)
from models.PyObjectID import PyObjectID
from models.User import User
from repository import NoteRepository
from text.CardSourceGenerator import CardSourceGenerator
from text.GPT import get_card_generation, get_single_card_generator
from text.GPT.GPTInterface import GPTInterface
from util.limitier import limiter

logger = logging.getLogger("logger")

USER_RATE_LIMIT = env_config.USER_RATE_LIMIT_PER_MINUTE

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


def map_notes_to_deck(notes: List[Dict]) -> Dict[str, Dict]:
    notes_by_deck_id: Dict[str, Dict] = {}

    for note in notes:
        deck_id = note["deck_id"]
        cards = note["cards"]

        notes_by_deck_id[deck_id] = {**note, "id": str(note["_id"]), "cards": cards}

    return notes_by_deck_id


async def get_or_create_openai_user(user_repo: DBInterface, userID: str) -> str:
    existing_open_ai_user: Dict = await user_repo.find_one({"user_id": userID})

    if not existing_open_ai_user:
        new_open_ai_user = User(user_id=userID, total_no_generated=1)
        result = await user_repo.insert_one(new_open_ai_user.dict(by_alias=True))
        open_ai_user_id = str(result.inserted_id)
    else:
        await user_repo.update_one(
            {"_id": existing_open_ai_user["_id"]}, {"$inc": {"total_no_generated": 1}}
        )
        open_ai_user_id = str(existing_open_ai_user["_id"])

    return open_ai_user_id


@router.post("", response_model=CardsResponse)
@limiter.limit(f"{USER_RATE_LIMIT}/minute")
async def generate_cards(
    # request needs to be there because of rate limiter
    request: Request,
    body: GenerateCardsRequest,
    userID: str,
    note_repo: Annotated[NoteRepository, Depends()],
    user_repo: DBInterface = Depends(get_user_repo),
    generate_cards: GPTInterface = Depends(get_card_generation),
    card_source_generator: CardSourceGenerator = Depends(get_card_source_generator),
):
    open_ai_user_id = await get_or_create_openai_user(user_repo, userID)

    text = body.text

    generated_cards = generate_cards(text, open_ai_user_id)

    cards_with_source = []

    for card in generated_cards:
        start_index, end_index = card_source_generator(text, card.question)

        card = Card(
            **card.dict(),
            source_start_index=start_index,
            source_end_index=end_index,
        )

        cards_with_source.append(card)

    note = Note(
        user_id=userID,
        deck_id=body.deck_id,
        text=text,
        cards_added=False,
        cards=cards_with_source,
        cards_edited_at=None,
        cards_edited=False,
    ).dict(by_alias=True)

    note["id"] = await note_repo.insert_one(note)

    data = CardsResponseData(**note)

    return CardsResponse(message="success", data=data)


@router.post(
    "/{id}/cards", response_model=AddedCardsResponse, response_model_by_alias=True
)
async def add_cards(
    id: str,
    deck_id: str,
    userID: str,
    note_repo: Annotated[NoteRepository, Depends()],
    deck_service: DeckServiceAPIInterface = Depends(get_deck_service),
):
    note = await note_repo.find_by_id(id, {"user_id": userID, "deck_id": deck_id})
    if not note:
        raise HTTPException(
            status_code=404, message="Failed to save cards", error="Note not found"
        )
    if note["cards_added"]:
        raise HTTPException(
            status_code=409, message="Failed to save cards", error="Cards Already added"
        )

    cards = note["cards"]

    try:
        cards = deck_service.save_cards(user_id=userID, deck_id=deck_id, cards=cards)
    except Exception as e:
        logger.error(f"Failed to save cards when sending request to deck service: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to save cards",
            error="Failed sending request to deck service",
        )

    await note_repo.update_one(
        {"_id": PyObjectID(id)},
        {"$set": {"cards_added": True}},
    )

    data = AddedCardsResponseData(cards=cards)

    return AddedCardsResponse(message="success", data=data)


@router.put("/{id}", response_model=UpdatedCardsResponse)
async def update_cards(
    id: str,
    body: UpdateCardsRequest,
    userID: str,
    note_repo: Annotated[NoteRepository, Depends()],
):
    new_cards = body.cards
    now = datetime.now().isoformat()

    await note_repo.update_one(
        {"_id": PyObjectID(id), "user_id": userID},
        {
            "$set": {
                "cards": [card.dict() for card in new_cards],
                "card_edited_at": now,
                "cards_edited": True,
            }
        },
    )

    data = UpdatedCardsResponseData(cards=new_cards)

    return UpdatedCardsResponse(message="Successfully updated cards", data=data)


@router.get("", response_model=NotesResponse)
async def get_note(
    userID: str,
    note_repo: Annotated[NoteRepository, Depends()],
):
    notes = await note_repo.query({"user_id": userID, "cards_added": False})

    notes_by_deck = map_notes_to_deck(notes)

    data = {key: NotesResponseData(**value) for key, value in notes_by_deck.items()}

    return NotesResponse(message="success", data=data)


@router.post("/{id}/card", response_model=CardResponse)
@limiter.limit(f"{USER_RATE_LIMIT}/minute")
async def generate_card(
    id: str,
    request: Request,
    body: GenerateCardRequest,
    userID: str,
    user_repo: DBInterface = Depends(get_user_repo),
    note_repo: DBInterface = Depends(get_note_repo),
    generate_card: GPTInterface = Depends(get_single_card_generator),
):
    openai_user_id = await get_or_create_openai_user(user_repo, userID)

    text = body.text

    generated_card: GPTCard = generate_card(
        text,
        openai_user_id,
    )

    now = datetime.now().isoformat()

    card = Card(
        **generated_card.dict(),
        source_start_index=body.source_start_index,
        source_end_index=body.source_end_index,
    )

    await note_repo.update_one(
        {"_id": PyObjectID(id), "user_id": userID},
        {
            "$set": {"cards_edited_at": now, "cards_edited": True},
            "$push": {"cards": {"$each": [card.dict(by_alias=True)], "$position": 0}},
        },
    )

    data = CardResponseData(id=id, text=text, card=card)
    return CardResponse(message="success", data=data)
