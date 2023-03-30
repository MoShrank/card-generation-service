from datetime import datetime, timedelta
from typing import List

from bson.objectid import ObjectId
from fastapi.testclient import TestClient

from dependencies import (
    get_card_generation,
    get_deck_service,
    get_note_repo,
    get_user_repo,
)
from external.CardGeneration import CardGenerationMock
from main import app
from models.Note import Card, DeckServiceCard
from util.AttrDict import AttrDict

client = TestClient(app)

OBJECT_ID = ObjectId()


class NoteRepoMock:
    async def query(self, query):
        return [
            {
                "_id": OBJECT_ID,
                "user_id": "1",
                "deck_id": "1",
                "text": "text",
                "cards": [
                    {
                        "created_at": datetime.now().isoformat(),
                        "cards_added": False,
                        "cards": [
                            {"question": "late", "answer": "late"},
                        ],
                    },
                    {
                        "created_at": (datetime.now() - timedelta(1)).isoformat(),
                        "cards_added": False,
                        "cards": [
                            {"question": "early", "answer": "early"},
                        ],
                    },
                ],
            },
        ]

    async def find_one(self, query):
        return None

    async def insert_one(self, document):
        insertion = AttrDict()
        insertion.update({"inserted_id": OBJECT_ID})
        return insertion

    async def update_one(self, query, update):
        pass


def get_note_repo_mock():
    return NoteRepoMock()


class UserRepoMock:
    async def find_one(self, query):
        return {"_id": OBJECT_ID, "user_id": "1"}

    async def update_one(self, query, update):
        pass


def get_user_repo_mock():
    return UserRepoMock()


class DeckServiceAPIMock:
    def save_cards(self, user_id: str, deck_id: str, cards: List[Card]):
        return [
            DeckServiceCard(
                **{"id": "1", "question": "late", "answer": "late", "deckID": "1"}
            ),
        ]


def get_deck_service_mock():
    return DeckServiceAPIMock()


def get_card_generation_mock():
    return CardGenerationMock()


app.dependency_overrides[get_note_repo] = get_note_repo_mock
app.dependency_overrides[get_user_repo] = get_user_repo_mock
app.dependency_overrides[get_deck_service] = get_deck_service_mock
app.dependency_overrides[get_card_generation] = get_card_generation_mock


def test_get_notes():
    response = client.get("/notes?userID=1")
    assert response.json()["data"] == {
        "1": {
            "id": str(OBJECT_ID),
            "cards": [
                {"question": "late", "answer": "late"},
            ],
            "text": "text",
        }
    }

    assert response.status_code == 200


def test_create_cards():
    expected_status_code = 200
    expeceted_data = {
        "id": str(OBJECT_ID),
        "text": "text",
        "cards": [
            {
                "question": "What is the capital of the United States?",
                "answer": "Washington D.C.",
            },
        ]
        * 3,
    }

    data = {
        "text": "text",
        "deck_id": "1",
    }
    response = client.post(f"/notes?userID={str(OBJECT_ID)}", json=data)
    response_data = response.json()["data"]
    print("response: ", response.json())
    assert response.status_code == expected_status_code
    assert response_data == expeceted_data


def test_create_cards_exceed_char_limit():
    expected_status_code = 422

    data = {
        "text": "t" * 3501,
        "deck_id": "1",
    }

    response = client.post(f"/notes?userID={str(OBJECT_ID)}", json=data)

    assert response.status_code == expected_status_code


def test_update_cards():
    expected_status_code = 200
    expected_data = {
        "cards": [
            {
                "question": "What is the capital of the United States?",
                "answer": "Washington D.C.",
            },
        ],
    }

    data = {
        "cards": [
            {
                "question": "What is the capital of the United States?",
                "answer": "Washington D.C.",
            },
        ],
    }

    response = client.put(f"/notes/{OBJECT_ID}?userID=1", json=data)

    assert response.status_code == expected_status_code
    assert response.json()["data"] == expected_data


def test_update_cards_empty_card():
    expected_status_code = 422

    data = {
        "cards": [
            {
                "question": "",
                "answer": "",
            }
        ],
    }

    response = client.put(f"/notes/{OBJECT_ID}?userID=1", json=data)

    assert response.status_code == expected_status_code


def test_add_cards():
    async def mockFindOne(self, query):
        return {
            "cards_added": False,
            "cards": [
                {
                    "cards": [
                        {
                            "question": "late",
                            "answer": "late",
                        }
                    ],
                    "deck_id": "1",
                    "created_at": datetime.now().isoformat(),
                },
            ],
        }

    NoteRepoMock.find_one = mockFindOne

    expected_status_code = 200
    expected_data = {
        "cards": [{"id": "1", "question": "late", "answer": "late", "deckID": "1"}]
    }

    response = client.post(f"/notes/{OBJECT_ID}/cards?userID=1&deck_id=1")

    assert response.status_code == expected_status_code
    assert response.json()["data"] == expected_data
