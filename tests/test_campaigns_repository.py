"""
Unit tests for the CampaignRepository class.

This test file demonstrates how to test repository logic that makes HTTP requests to external services.
We use pytest's monkeypatch fixture to mock httpx.AsyncClient.get so that no real HTTP requests are made.

Key concepts:
- Use monkeypatch to replace external network calls with controlled mock responses.
- Test both the successful and error cases for robust code.
"""
import pytest
import httpx
from typing import Any
from services.profiles.repository.campaigns import CampaignRepository
from services.profiles.repository.campaigns_types import Campaign

@pytest.mark.asyncio
async def test_get_active_campaigns_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that get_active_campaigns returns campaign data when the HTTP request succeeds.
    Mocks httpx.AsyncClient.get to return a controlled response.
    """
    async def mock_get(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            def raise_for_status(self) -> None:
                pass
            async def json(self) -> list[Campaign]:
                return [{"id": 1, "name": "test"}]
        return MockResponse()
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
    repo = CampaignRepository()
    campaigns = await repo.get_active_campaigns()
    assert campaigns == [{"id": 1, "name": "test"}]

@pytest.mark.asyncio
async def test_get_active_campaigns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that get_active_campaigns raises an error when the HTTP request fails.
    Mocks httpx.AsyncClient.get to simulate an HTTP error.
    """
    async def mock_get(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            def raise_for_status(self) -> None:
                raise httpx.HTTPStatusError("error", request=None, response=None)
            async def json(self) -> None:
                return None
        return MockResponse()
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
    repo = CampaignRepository()
    with pytest.raises(httpx.HTTPStatusError):
        await repo.get_active_campaigns()
