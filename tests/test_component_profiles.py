import pytest
from fastapi.testclient import TestClient
from services.profiles.main import app

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

class MockProfileService:
    def __init__(self, *args, **kwargs):
        pass
    async def get_client_config(self, player_id: str):
        if player_id == "9001":
            return {
                "player_id": "9001",
                "name": "Test",
                "level": 1,
                "active_campaigns": mock_campaigns_response
            }
        return None

@pytest.fixture(autouse=True)
def override_service_dependency():
    from services.profiles.dependencies import get_service
    app.dependency_overrides[get_service] = lambda: MockProfileService()
    yield
    app.dependency_overrides.clear()

def test_get_client_config_returns_non_empty_profile():
    with TestClient(app) as client:
        player_id = "9001"
        response = client.get(f"/get_client_config/{player_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_id
        assert "active_campaigns" in data
        assert data["active_campaigns"] == mock_campaigns_response
