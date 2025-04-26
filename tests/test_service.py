import hypothesis
import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, Mock
from hypothesis.strategies import from_type
from services.profiles.service import level_matcher, has_matcher, does_not_have_matcher, match_campaign
from services.profiles.repository.profiles_types import Profile
from services.profiles.repository.campaigns_types import Campaign, Matchers, LevelMatcher, HasMatcher, DoesNotHaveMatcher
from services.profiles.service import ProfileService

hypothesis.settings.register_profile('fast', max_examples=3)
hypothesis.settings.load_profile('fast')#

st_profile = from_type(Profile)
st_campaign = from_type(Campaign)

def with_matchers(campaign: Campaign, matchers: Matchers):
    return campaign.model_copy(update={'matchers': matchers})

@given(st_profile, st_campaign)
def test_level_matcher_in_range(profile: Profile, campaign:Campaign):
    campaign = with_matchers(campaign, Matchers(level=LevelMatcher(min=1, max=10)))
    profile = profile.model_copy(update={'level': 5})
    assert level_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_level_matcher_out_of_range(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(level=LevelMatcher(min=5, max=10)))
    profile = profile.model_copy(update={'level': 3})
    assert not level_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_has_matcher_country_pass(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(has=HasMatcher(country=['US', 'FR'])))
    profile = profile.model_copy(update={'country': 'FR'})
    assert has_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_has_matcher_country_fail(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(has=HasMatcher(country=['US', 'FR'])))
    profile = profile.model_copy(update={'country': 'DE'})
    assert not has_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_has_matcher_items_pass(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(has=HasMatcher(items=['sword', 'shield'])))
    profile = profile.model_copy(update={'inventory': {'sword': 1, 'shield': 2}})
    assert has_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_has_matcher_items_fail(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(has=HasMatcher(items=['sword', 'shield'])))
    profile = profile.model_copy(update={'inventory': {'sword': 1}})
    assert not has_matcher(profile, campaign)

def inventory_without_forbidden(forbidden):
    """Strategy for inventory dicts where forbidden is either absent or set to 0."""
    return st.dictionaries(
        keys=st.text(min_size=1, max_size=10).filter(lambda k: k != forbidden),
        values=st.integers(min_value=1, max_value=10),
        max_size=5
    ).flatmap(lambda inv: st.one_of(
        st.just(inv),
        st.just({**inv, forbidden: 0})
    ))

@given(
    profile=st_profile,
    campaign=st_campaign,
    inventory=inventory_without_forbidden('sword')
)
def test_does_not_have_matcher_pass(profile: Profile, campaign: Campaign, inventory):
    forbidden = 'sword'
    campaign = with_matchers(campaign, Matchers(does_not_have=DoesNotHaveMatcher(items=[forbidden])))
    profile = profile.model_copy(update={'inventory': inventory})
    assert does_not_have_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_does_not_have_matcher_fail(profile: Profile, campaign: Campaign):
    forbidden = 'sword'
    campaign = with_matchers(campaign, Matchers(does_not_have=DoesNotHaveMatcher(items=[forbidden])))
    profile = profile.model_copy(update={'inventory': {forbidden: 1}})
    assert not does_not_have_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_match_campaign_all_match(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(
        level=LevelMatcher(min=1, max=10),
        has=HasMatcher(country=['US'], items=['sword']),
        does_not_have=DoesNotHaveMatcher(items=['bow'])
    ))
    profile = profile.model_copy(update={'level': 5, 'country': 'US', 'inventory': {'sword': 1, 'bow': 0}})
    assert match_campaign(profile, campaign)

@given(st_profile, st_campaign)
def test_match_campaign_one_fails(profile: Profile, campaign:Campaign):
    campaign = with_matchers(campaign, Matchers(
        level=LevelMatcher(min=1, max=10),
        has=HasMatcher(country=['US'], items=['sword']),
        does_not_have=DoesNotHaveMatcher(items=['bow'])
    ))
    profile = profile.model_copy(update={'level': 5, 'country': 'US', 'inventory': {'sword': 1, 'bow': 2}})
    assert not match_campaign(profile, campaign)

@pytest.mark.asyncio
@given(profile=st_profile, campaign=st_campaign)
async def test_get_client_config_profile_found_campaigns_matched(profile: Profile, campaign: Campaign):
    campaign = campaign.model_copy(update={"matchers": Matchers()})
    profile_repo = Mock(get_profile_by_player_id=AsyncMock(return_value=profile))
    campaign_repo = Mock(get_active_campaigns=AsyncMock(return_value=[campaign]))
    service = ProfileService(profile_repo, campaign_repo)
    result = await service.get_client_config(profile.player_id)
    assert result is not None
    assert campaign.name in result.active_campaigns

@pytest.mark.asyncio
@given(player_id=st.text(min_size=1, max_size=32))
async def test_get_client_config_profile_not_found(player_id: str):
    profile_repo = Mock(get_profile_by_player_id=AsyncMock(return_value=None))
    campaign_repo = Mock(get_active_campaigns=AsyncMock())
    service = ProfileService(profile_repo, campaign_repo)
    result = await service.get_client_config(player_id)
    assert result is None

@pytest.mark.asyncio
@given(profile=st_profile, campaign=st_campaign)
async def test_get_client_config_profile_found_no_campaigns_matched(profile: Profile, campaign: Campaign):
    campaign = campaign.model_copy(update={"matchers": Matchers(level=LevelMatcher(min=999, max=1000))})
    profile = profile.model_copy(update={"level": 0})
    profile_repo = Mock(get_profile_by_player_id=AsyncMock(return_value=profile))
    campaign_repo = Mock(get_active_campaigns=AsyncMock(return_value=[campaign]))
    service = ProfileService(profile_repo, campaign_repo)
    result = await service.get_client_config(profile.player_id)
    assert result is not None
    assert result.active_campaigns == []
