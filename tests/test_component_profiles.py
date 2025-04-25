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

async def mock_get_campaigns():
    return mock_campaigns_response

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


def test_get_client_config_returns_non_empty_profile(mock_campaigns, monkeypatch):
    async def mock_get_profile_by_player_id(db, player_id):
        if player_id == "9001":
            return {"player_id": "9001", "name": "Test", "level": 1}
        return None
    monkeypatch.setattr("services.profiles.repository.get_profile_by_player_id", mock_get_profile_by_player_id)
    monkeypatch.setattr("services.profiles.repository.get_active_campaigns", mock_get_campaigns)
    with TestClient(app) as client:
        player_id = "9001"
        response = client.get(f"/get_client_config/{player_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_id
        assert "active_campaigns" in data
        assert data["active_campaigns"] == mock_campaigns_response
