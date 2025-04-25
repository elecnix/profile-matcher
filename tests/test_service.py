"""
Unit tests for the ProfileService class (business logic layer).

This test file demonstrates how to test service/business logic in isolation by mocking repository dependencies with AsyncMock.

Key concepts:
- Use AsyncMock to create fake repository objects that return controlled results.
- Test service logic without touching the database or external APIs.
- Verify both the happy path and edge cases (e.g., profile not found).

Each test focuses on a different matcher property (level, country, has.items, does_not_have.items)
using hypothesis strategies for Profile and Campaign.
"""
import pytest
from unittest.mock import AsyncMock
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import from_type
from services.profiles.repository.profiles import ProfileRepository
from services.profiles.repository.campaigns import CampaignRepository
from services.profiles.service import ProfileService
from services.profiles.repository.profiles_types import Profile
from services.profiles.repository.campaigns_types import Campaign, Matchers, LevelMatcher, HasMatcher, DoesNotHaveMatcher

settings.register_profile("fast", max_examples=10)
settings.load_profile("fast")

profile_base_strategy = from_type(Profile)
campaign_base_strategy = from_type(Campaign)

# Helper to build a campaign with a specific matcher

def campaign_with_matchers(**matcher_kwargs):
    return campaign_base_strategy.map(
        lambda campaign: campaign.model_copy(update={"matchers": Matchers(**matcher_kwargs)})
    )

async def run_service_with_profile_and_campaigns(profile: Profile, campaigns: list[Campaign]):
    """
    Helper to run ProfileService.get_client_config with given profile and campaigns.
    """
    mock_profile_repo = AsyncMock(ProfileRepository)
    mock_campaign_repo = AsyncMock(CampaignRepository)
    mock_profile_repo.get_profile_by_player_id.return_value = profile
    mock_campaign_repo.get_active_campaigns.return_value = campaigns
    service = ProfileService(mock_profile_repo, mock_campaign_repo)
    return await service.get_client_config(profile.player_id)

@pytest.mark.asyncio
async def test_get_client_config_profile_not_found():
    """
    Test that get_client_config returns None when the profile is not found.
    """
    mock_profile_repo = AsyncMock(ProfileRepository)
    mock_campaign_repo = AsyncMock(CampaignRepository)
    mock_profile_repo.get_profile_by_player_id.return_value = None
    service = ProfileService(mock_profile_repo, mock_campaign_repo)
    result = await service.get_client_config("notfound")
    assert result is None

min_max_level = st.integers(min_value=1, max_value=100).flatmap(
    lambda min_level: st.tuples(st.just(min_level), st.integers(min_value=min_level, max_value=100))
)

level_matcher_strategy = min_max_level.flatmap(
    lambda min_max: campaign_base_strategy.map(
        lambda campaign: campaign.model_copy(update={"matchers": Matchers(level=LevelMatcher(min=min_max[0], max=min_max[1]))})
    )
)

@pytest.mark.asyncio
@given(
    profile=profile_base_strategy,
    campaign=level_matcher_strategy
)
async def test_level_matcher(profile: Profile, campaign: Campaign):
    result = await run_service_with_profile_and_campaigns(profile, [campaign])
    in_range = campaign.matchers.level.min <= profile.level <= campaign.matchers.level.max
    if in_range:
        assert campaign.name in result.active_campaigns
    else:
        assert campaign.name not in result.active_campaigns

@pytest.mark.asyncio
@given(
    profile=profile_base_strategy,
    country=st.text(min_size=2, max_size=2),
    campaign=campaign_base_strategy
)
async def test_country_matcher(profile: Profile, country: str, campaign: Campaign):
    campaign = campaign.model_copy(update={"matchers": Matchers(country=[country])})
    profile = profile.model_copy(update={"country": country})
    result = await run_service_with_profile_and_campaigns(profile, [campaign])
    assert campaign.name in result.active_campaigns

@pytest.mark.asyncio
@given(
    profile=profile_base_strategy,
    item=st.text(min_size=1, max_size=10),
    campaign=campaign_base_strategy
)
async def test_has_items_matcher(profile: Profile, item: str, campaign: Campaign):
    campaign = campaign.model_copy(update={"matchers": Matchers(has=HasMatcher(items=[item]))})
    profile = profile.model_copy(update={"inventory": {item: 1}})
    result = await run_service_with_profile_and_campaigns(profile, [campaign])
    assert campaign.name in result.active_campaigns

@pytest.mark.asyncio
@given(
    profile=profile_base_strategy,
    forbidden_item=st.text(min_size=1, max_size=10),
    campaign=campaign_base_strategy
)
async def test_does_not_have_items_matcher(profile: Profile, forbidden_item: str, campaign: Campaign):
    campaign = campaign.model_copy(update={"matchers": Matchers(does_not_have=DoesNotHaveMatcher(items=[forbidden_item]))})
    profile = profile.model_copy(update={"inventory": {forbidden_item: 1}})
    result = await run_service_with_profile_and_campaigns(profile, [campaign])
    assert campaign.name not in result.active_campaigns
