from datetime import datetime, timedelta

from bson.objectid import ObjectId
from dependencies import get_note_repo, get_user_repo
from fastapi.testclient import TestClient
from main import app
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


app.dependency_overrides[get_note_repo] = get_note_repo_mock
app.dependency_overrides[get_user_repo] = get_user_repo_mock


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
        ],
    }

    data = {
        "text": "text",
        "deck_id": "1",
    }
    response = client.post(f"/notes?userID={str(OBJECT_ID)}", json=data)
    response_data = response.json()["data"]

    assert response.status_code == expected_status_code
    assert response_data == expeceted_data


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

    response = client.put("/notes/1?userID=1", json=data)

    assert response.status_code == expected_status_code
    assert response.json()["data"] == expected_data


def test_add_cards():
    pass
