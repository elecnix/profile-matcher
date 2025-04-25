from hypothesis import given, strategies as st
from hypothesis.strategies import from_type
from services.profiles.service import level_matcher, has_matcher, does_not_have_matcher, match_campaign
from services.profiles.repository.profiles_types import Profile
from services.profiles.repository.campaigns_types import Campaign, Matchers, LevelMatcher, HasMatcher, DoesNotHaveMatcher

st_profile = from_type(Profile)
st_campaign = from_type(Campaign)

def with_matchers(campaign, matchers: Matchers):
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

@given(st_profile, st_campaign)
def test_does_not_have_matcher_pass(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(does_not_have=DoesNotHaveMatcher(items=['bow'])))
    profile = profile.model_copy(update={'inventory': {'sword': 1}})
    assert does_not_have_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_does_not_have_matcher_fail(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(does_not_have=DoesNotHaveMatcher(items=['sword'])))
    profile = profile.model_copy(update={'inventory': {'sword': 1}})
    assert not does_not_have_matcher(profile, campaign)

@given(st_profile, st_campaign)
def test_match_campaign_all_match(profile: Profile, campaign: Campaign):
    campaign = with_matchers(campaign, Matchers(
        level=LevelMatcher(min=1, max=10),
        has=HasMatcher(country=['US'], items=['sword']),
        does_not_have=DoesNotHaveMatcher(items=['bow'])
    ))
    profile = profile.model_copy(update={'level': 5, 'country': 'US', 'inventory': {'sword': 1}})
    assert match_campaign(profile, campaign)

@given(st_profile, st_campaign)
def test_match_campaign_one_fails(profile:Profile, campaign:Campaign):
    campaign = with_matchers(campaign, Matchers(
        level=LevelMatcher(min=1, max=10),
        has=HasMatcher(country=['US'], items=['sword']),
        does_not_have=DoesNotHaveMatcher(items=['bow'])
    ))
    profile = profile.model_copy(update={'level': 5, 'country': 'US', 'inventory': {'sword': 1, 'bow': 2}})
    assert not match_campaign(profile, campaign)
