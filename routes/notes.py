import logging
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, Request

from config import env_config
from database.db_interface import DBInterface
from dependencies import (
    get_card_generation,
    get_card_source_generator,
    get_deck_service,
    get_note_repo,
    get_user_repo,
)
from external.CardGeneration import CardGenerationInterface
from external.DeckServiceAPI import DeckServiceAPIInterface
from models.HttpModels import HTTPException
from models.Note import (
    AddedCardsResponse,
    Card,
    Cards,
    CardsResponse,
    GenerateCardsRequest,
    Note,
    NotesResponse,
    UpdateCardsRequest,
    UpdatedCardsResponse,
)
from models.PyObjectID import PyObjectID
from models.User import User
from text.CardSourceGenerator import CardSourceGenerator
from util.limitier import limiter

logger = logging.getLogger("logger")

USER_RATE_LIMIT = env_config.USER_RATE_LIMIT_PER_MINUTE

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


def get_latest_cards_from_note(note: Dict) -> List[Card]:
    cards = sorted(note["cards"], key=lambda x: x["created_at"], reverse=True)[0][
        "cards"
    ]

    return cards


def map_notes_to_deck(notes: List[Dict]) -> Dict[str, Dict]:
    notes_by_deck_id: Dict[str, Dict] = {}

    for note in notes:
        deck_id = note["deck_id"]
        cards = get_latest_cards_from_note(note)

        notes_by_deck_id[deck_id] = {**note, "id": str(note["_id"]), "cards": cards}

    return notes_by_deck_id


@router.post("", response_model=CardsResponse)
@limiter.limit(f"{USER_RATE_LIMIT}/minute")
async def generate_cards(
    # request needs to be there because of rate limiter
    request: Request,
    body: GenerateCardsRequest,
    userID: str,
    user_repo: DBInterface = Depends(get_user_repo),
    note_repo: DBInterface = Depends(get_note_repo),
    generate_cards: CardGenerationInterface = Depends(get_card_generation),
    card_source_generator: CardSourceGenerator = Depends(get_card_source_generator),
):
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

    cards = Cards(
        cards=cards_with_source,
        cards_added=False,
        original_cards=True,
        created_at=datetime.now().isoformat(),
    )

    document = Note(
        user_id=userID,
        deck_id=body.deck_id,
        text=text,
        cards_added=False,
        cards=[cards],
        created_at=datetime.now().isoformat(),
    ).dict(by_alias=True)

    insertion_result = await note_repo.insert_one(document)
    note_id = str(insertion_result.inserted_id)

    document["id"] = note_id

    return CardsResponse(message="success", data={**document, "cards": cards.cards})


@router.post(
    "/{id}/cards", response_model=AddedCardsResponse, response_model_by_alias=True
)
async def add_cards(
    id: str,
    deck_id: str,
    userID: str,
    note_repo: DBInterface = Depends(get_note_repo),
    deck_service: DeckServiceAPIInterface = Depends(get_deck_service),
):
    note: Dict = await note_repo.find_one(
        {"_id": PyObjectID(id), "user_id": userID, "deck_id": deck_id}
    )

    if not note:
        raise HTTPException(
            status_code=404, message="Failed to save cards", error="Note not found"
        )

    if note["cards_added"]:
        raise HTTPException(
            status_code=409, message="Failed to save cards", error="Cards Already added"
        )

    cards = get_latest_cards_from_note(note)

    try:
        cards = deck_service.save_cards(user_id=userID, deck_id=deck_id, cards=cards)
    except Exception as e:
        logger.error(f"Failed to save cards when sending request to deck service: {e}")
        raise HTTPException(
            status_code=500,
            message="Failed to save cards",
            error=f"Failed sending request to deck service",
        )

    await note_repo.update_one(
        {"_id": PyObjectID(id)},
        {"$set": {"cards_added": True}},
    )

    return AddedCardsResponse(message="success", data={"cards": cards})


@router.put("/{id}", response_model=UpdatedCardsResponse)
async def update_cards(
    id: str,
    body: UpdateCardsRequest,
    userID: str,
    note_repo: DBInterface = Depends(get_note_repo),
):
    cards = Cards(
        cards=body.cards,
        cards_added=False,
        original_cards=False,
        created_at=datetime.now().isoformat(),
    )

    await note_repo.update_one(
        {"_id": PyObjectID(id), "user_id": userID}, {"$push": {"cards": cards.dict()}}
    )

    return UpdatedCardsResponse(
        message="Successfully updated cards", data={"cards": cards.cards}
    )


@router.get("", response_model=NotesResponse)
async def get_note(
    userID: str,
    note_repo: DBInterface = Depends(get_note_repo),
):
    notes: List[Dict] = await note_repo.query({"user_id": userID, "cards_added": False})

    notes_by_deck = map_notes_to_deck(notes)

    return NotesResponse(message="success", data=notes_by_deck)
