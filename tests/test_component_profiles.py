import pytest
from fastapi.testclient import TestClient
from services.profiles.main import app

client = TestClient(app)

# Mock response for the campaigns service
mock_campaigns_response = [
    {
        "game": "mygame",
        "name": "mycampaign",
        "priority": 10.5,
        "matchers": {
            "level": {"min": 1, "max": 3},
            "has": {"country": ["US", "RO", "CA"], "items": ["item_1"]},
            "does_not_have": {"items": ["item_4"]}
        },
        "start_date": "2022-01-25 00:00:00Z",
        "end_date": "2022-02-25 00:00:00Z",
        "enabled": True,
        "last_updated": "2021-07-13 11:46:58Z"
    }
]

@pytest.fixture
def mock_campaigns(monkeypatch):
    import requests
    class MockResponse:
        def json(self):
            return mock_campaigns_response
        @property
        def status_code(self):
            return 200
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())

@pytest.fixture
def mock_mongo_client():
    class MockCollection:
        async def find_one(self, query):
            if query.get("player_id") == "9001":
                return {"player_id": "9001", "name": "Test", "level": 1, "_id": "mockid"}
            return None
    class MockDB:
        def __getitem__(self, name):
            return MockCollection()
    class MockClient:
        def __getitem__(self, name):
            return MockDB()
    return MockClient()

from services.profiles.main import get_mongo_client

def test_get_client_config_returns_non_empty_profile(mock_campaigns, mock_mongo_client):
    app.dependency_overrides[get_mongo_client] = lambda: mock_mongo_client
    with TestClient(app) as client:
        player_id = "9001"
        response = client.get(f"/get_client_config/{player_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == "9001"
    app.dependency_overrides = {}
