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
import datetime
from typing import Any
from services.profiles.repository.campaigns import CampaignRepository
from services.profiles.repository.campaigns_types import Campaign
from hypothesis import given
from unittest.mock import patch
from hypothesis.strategies import from_type
import pytest_asyncio

campaign_strategy = from_type(Campaign)

@pytest_asyncio.fixture(autouse=True)
def patch_fetch_campaigns(monkeypatch):
    # Patch the _fetch_campaigns method to remove the aiocache decorator for tests
    orig = CampaignRepository._fetch_campaigns.__wrapped__
    monkeypatch.setattr(CampaignRepository, "_fetch_campaigns", orig)

def make_mock_get(called, campaign):
    async def mock_get(self, url, params=None, **kwargs):
        called['url'] = url
        called['params'] = params or {}
        class MockResponse:
            def raise_for_status(self) -> None:
                pass
            def json(self) -> list:
                return [campaign.model_dump()]
        return MockResponse()
    return mock_get

from hypothesis.strategies import datetimes

@pytest.mark.asyncio
@given(
    campaign=campaign_strategy,
    start=datetimes(),
    end=datetimes()
)
async def test_get_active_campaigns_success_explicit_interval(campaign: Campaign, start: datetime.datetime, end: datetime.datetime) -> None:
    """
    Test that get_active_campaigns returns campaign data and passes explicit interval params.
    """
    called = {}
    with patch("httpx.AsyncClient.get", make_mock_get(called, campaign)):
        repo = CampaignRepository()
        await repo.get_active_campaigns(start, end)
        assert 'params' in called, f"Mock was not called, got called={called} for campaign={campaign!r}"
        assert called['params']['start_date'] == start.isoformat()
        assert called['params']['end_date'] == end.isoformat()

@pytest.mark.asyncio
@given(campaign_strategy)
async def test_get_active_campaigns_success_default_interval(campaign: Campaign) -> None:
    """
    Test that get_active_campaigns returns campaign data and passes default interval params.
    """
    called = {}
    with patch("httpx.AsyncClient.get", make_mock_get(called, campaign)):
        repo = CampaignRepository()
        await repo.get_active_campaigns()
        assert 'start_date' in called['params']
        assert 'end_date' in called['params']

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
            def json(self) -> None:
                return None
        return MockResponse()
    with patch("httpx.AsyncClient.get", mock_get):
        repo = CampaignRepository()
        with pytest.raises(httpx.HTTPStatusError):
            await repo.get_active_campaigns()

make_invalid_campaign = lambda c: c.model_copy(update={"game": None})

@pytest.mark.asyncio
@given(campaign_strategy.map(make_invalid_campaign))
async def test_get_active_campaigns_invalid_campaign(invalid_campaign: Campaign) -> None:
    """
    Test that get_active_campaigns raises a ValidationError when the HTTP response contains an invalid campaign, in this case where 'game' is None.
    Uses Hypothesis to generate invalid campaigns by setting a required field to None.
    """
    async def mock_get(*args: Any, **kwargs: Any) -> Any:
        class MockResponse:
            def raise_for_status(self) -> None:
                pass
            def json(self) -> list:
                return [invalid_campaign.model_dump()]
        return MockResponse()
    with patch("httpx.AsyncClient.get", mock_get):
        repo = CampaignRepository()
        with pytest.raises(pydantic.ValidationError):
            await repo.get_active_campaigns()
