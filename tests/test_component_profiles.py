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


def test_get_client_config_returns_non_empty_profile(mock_campaigns):
    player_id = "test_player"
    response = client.get(f"/get_client_config/{player_id}")
    assert response.status_code == 200
    profile = response.json()
    # Fails: profile is empty
    assert profile, "Expected non-empty profile, got empty profile!"
