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
from hypothesis import given, strategies as st
from services.profiles.repository.profiles_types import Profile

from typing import Callable

from contextlib import contextmanager

# Generate a player ID that is a valid URL parameter
st_player_id = st.text(
    alphabet=st.characters(
        whitelist_categories=('L', 'N'),  # Letters and digits
        whitelist_characters="-_",
    ),
    min_size=1,
    max_size=32,
)

@contextmanager
def inject_profile_service(profile_lambda: Callable[[str], object]):
    class MockProfileService:
        async def get_client_config(self, player_id: str):
            return profile_lambda(player_id)
    from services.profiles.dependencies import get_service
    app.dependency_overrides[get_service] = lambda: MockProfileService()
    try:
        yield
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
@given(profile=st.builds(Profile, player_id=st_player_id))
async def test_endpoint_get_client_config_success(profile: Profile):
    """
    Test that the endpoint returns a profile.
    """
    with inject_profile_service(lambda player_id: profile):
        with TestClient(app) as client:
            response = client.get(f"/get_client_config/{profile.player_id}")
            assert response.status_code == 200
            assert response.json() == profile.model_dump()

@pytest.mark.asyncio
@given(profile=st.builds(Profile, player_id=st_player_id))
async def test_endpoint_get_client_config_not_found(profile: Profile):
    """
    Test that the endpoint returns a 404 error.
    """
    with inject_profile_service(lambda player_id: None):
        with TestClient(app) as client:
            response = client.get(f"/get_client_config/{profile.player_id}")
            assert response.status_code == 404
            assert response.json()["detail"] == "Profile not found"

@pytest.mark.asyncio
@given(profile=st.builds(Profile, player_id=st_player_id))
async def test_endpoint_get_client_config_exception(profile: Profile):
    """
    Test that the endpoint responds with HTTP 500.
    Covers the except/logging path in the endpoint.
    """
    with inject_profile_service(lambda player_id: (_ for _ in ()).throw(RuntimeError("simulated service failure"))):
        with TestClient(app) as client:
            response = client.get(f"/get_client_config/{profile.player_id}")
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal server error"
