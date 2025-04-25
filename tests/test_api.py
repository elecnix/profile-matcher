"""
Integration tests for the /get_client_config/{player_id} FastAPI endpoint.

This test file demonstrates how to test FastAPI endpoints using TestClient and dependency overrides.

Key concepts:
- Use FastAPI's dependency_overrides to inject a mock service layer for controlled endpoint behavior.
- Use TestClient to simulate HTTP requests to the API.
- Test both successful and error responses from the endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from services.profiles.main import app

mock_profile = {
    "player_id": "9001",
    "name": "Test",
    "level": 1,
    "active_campaigns": [{"id": 1}]
}

class MockProfileService:
    async def get_client_config(self, player_id: str):
        if player_id == "9001":
            return mock_profile
        return None

@pytest.fixture(autouse=True)
def override_service_dependency():
    from services.profiles.dependencies import get_service
    app.dependency_overrides[get_service] = lambda: MockProfileService()
    yield
    app.dependency_overrides.clear()

def test_endpoint_get_client_config_success():
    """
    Test that the endpoint returns a profile when the player exists.
    Uses a mock ProfileService via dependency override.
    """
    with TestClient(app) as client:
        response = client.get("/get_client_config/9001")
        assert response.status_code == 200
        assert response.json() == mock_profile

def test_endpoint_get_client_config_not_found():
    """
    Test that the endpoint returns a 404 error when the profile is not found.
    Uses a mock ProfileService via dependency override.
    """
    with TestClient(app) as client:
        response = client.get("/get_client_config/404")
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile not found"

def test_endpoint_get_client_config_exception(monkeypatch):
    """
    Test that the endpoint logs and returns 404 when an exception is raised in the service.
    Covers the except/logging path in the endpoint.
    """
    class ExceptionService:
        async def get_client_config(self, player_id):
            raise RuntimeError("simulated service failure")
    from services.profiles.dependencies import get_service
    app.dependency_overrides[get_service] = lambda: ExceptionService()
    with TestClient(app) as client:
        response = client.get("/get_client_config/any")
        assert response.status_code == 404
        assert response.json()["detail"] == "Profile not found"
    app.dependency_overrides.clear()
