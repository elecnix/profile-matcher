"""
Unit tests for the ProfileService class (business logic layer).

This test file demonstrates how to test service/business logic in isolation by mocking repository dependencies with AsyncMock.

Key concepts:
- Use AsyncMock to create fake repository objects that return controlled results.
- Test service logic without touching the database or external APIs.
- Verify both the happy path and edge cases (e.g., profile not found).
"""
import pytest
from unittest.mock import AsyncMock
from services.profiles.service import ProfileService

@pytest.mark.asyncio
async def test_get_client_config_profile_found():
    """
    Test that get_client_config injects campaigns when the profile is found.
    """
    mock_profile_repo = AsyncMock()
    mock_campaign_repo = AsyncMock()
    mock_profile_repo.get_profile_by_player_id.return_value = {"player_id": "42"}
    mock_campaign_repo.get_active_campaigns.return_value = [{"id": 1}]
    service = ProfileService(mock_profile_repo, mock_campaign_repo)
    result = await service.get_client_config("42")
    assert result["player_id"] == "42"
    assert result["active_campaigns"] == [{"id": 1}]

@pytest.mark.asyncio
async def test_get_client_config_profile_not_found():
    """
    Test that get_client_config returns None when the profile is not found.
    """
    mock_profile_repo = AsyncMock()
    mock_campaign_repo = AsyncMock()
    mock_profile_repo.get_profile_by_player_id.return_value = None
    service = ProfileService(mock_profile_repo, mock_campaign_repo)
    result = await service.get_client_config("notfound")
    assert result is None
