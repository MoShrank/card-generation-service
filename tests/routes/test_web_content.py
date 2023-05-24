import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from dependencies import get_web_content_repo
from main import app
from models.WebContent import WebContentRequest

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user_id():
    return "test_user_id"


@pytest.fixture(scope="module")
def test_web_content_request():
    return WebContentRequest(
        url="https://www.example.com",
        name="Test Web Content",
        summarise=True,
    )


"""
def test_create_post(test_db, test_user_id, test_web_content_request):
    response = client.post(
        f"/web-content/post?userID={test_user_id}",
        json=test_web_content_request.dict(),
    )
    assert response.status_code == 200
    assert response.json()["message"] == "succes"
    assert response.json()["data"]["url"] == test_web_content_request.url
"""

OBJECT_ID = ObjectId()


class WebContentRepoMock:
    def __init__(self):
        self.web_content = []

    async def insert(self, web_content):
        self.web_content.append(web_content)

    async def query(self, query):
        return [
            {
                "_id": OBJECT_ID,
                "url": "https://www.example.com",
                "name": "Test Web Content",
                "summarise": True,
                "created_at": "2021-01-01 00:00:00",
            }
        ]


def get_web_content_repo_mock():
    return WebContentRepoMock()


app.dependency_overrides[get_web_content_repo] = get_web_content_repo_mock


def test_get_posts(test_user_id, test_web_content_request):
    response = client.get(f"/web-content/post?userID={test_user_id}")

    data = response.json()["data"]

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully retrieved webpages"
    assert len(data) == 1
    assert data[0]["url"] == test_web_content_request.url
    assert "id" in data[0]
    assert isinstance(data[0]["id"], str)
