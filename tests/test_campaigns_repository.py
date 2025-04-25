"""
Unit tests for the CampaignRepository class.

This test file demonstrates how to test repository logic that makes HTTP requests to external services.
We use pytest's monkeypatch fixture to mock httpx.AsyncClient.get so that no real HTTP requests are made.

Key concepts:
- Use monkeypatch to replace external network calls with controlled mock responses.
- Test both the successful and error cases for robust code.
"""
import httpx
import pydantic
import pytest
from typing import Any
from services.profiles.repository.campaigns import CampaignRepository
from services.profiles.repository.campaigns_types import Campaign
from hypothesis import given
from unittest.mock import patch
from hypothesis.strategies import from_type

campaign_strategy = from_type(Campaign)

@pytest.mark.asyncio
@given(campaign_strategy)
async def test_get_active_campaigns_success(campaign: Campaign) -> None:
    """
    Test that get_active_campaigns returns campaign data when the HTTP request succeeds.
    Uses Hypothesis to generate campaigns.
    """
    async def mock_get(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            def raise_for_status(self) -> None:
                pass
            async def json(self) -> list:
                return [campaign.model_dump()]
        return MockResponse()
    with patch("httpx.AsyncClient.get", mock_get):
        repo = CampaignRepository()
        campaigns = await repo.get_active_campaigns()
        assert [c.model_dump() for c in campaigns] == [campaign.model_dump()]

@pytest.mark.asyncio
async def test_get_active_campaigns_error() -> None:
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
    with patch("httpx.AsyncClient.get", mock_get):
        repo = CampaignRepository()
        with pytest.raises(httpx.HTTPStatusError):
            await repo.get_active_campaigns()

@pytest.mark.asyncio
@given(campaign_strategy.map(lambda c: c.model_copy(update={"game": None})))
async def test_get_active_campaigns_invalid_campaign(invalid_campaign: Campaign) -> None:
    """
    Test that get_active_campaigns raises a ValidationError when the HTTP response contains an invalid campaign, in this case where 'game' is None.
    Uses Hypothesis to generate invalid campaigns by setting a required field to None.
    """
    async def mock_get(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            def raise_for_status(self) -> None:
                pass
            async def json(self) -> list:
                return [invalid_campaign.model_dump()]
        return MockResponse()
    with patch("httpx.AsyncClient.get", mock_get):
        repo = CampaignRepository()
        with pytest.raises(pydantic.ValidationError):
            await repo.get_active_campaigns()
