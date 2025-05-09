from typing import Optional
from services.profiles.repository.campaigns_types import Campaign
from services.profiles.repository.profiles_types import Profile
from services.profiles.repository.profiles import ProfileRepository
from services.profiles.repository.campaigns import CampaignRepository

class ProfileService:
    def __init__(self, profile_repository: ProfileRepository, campaign_repository: CampaignRepository):
        self._profile_repository = profile_repository
        self._campaign_repository = campaign_repository

    async def get_client_config(self, player_id: str) -> Optional[Profile]:
        profile = await self._profile_repository.get_profile_by_player_id(player_id)
        if not profile:
            return None
        campaigns = await self._campaign_repository.get_active_campaigns()
        matched_campaigns = [c.name for c in campaigns if match_campaign(profile, c)]
        profile.active_campaigns = matched_campaigns
        return profile

def level_matcher(profile: Profile, campaign: Campaign) -> bool:
    matchers = campaign.matchers
    if matchers.level:
        return matchers.level.min <= profile.level <= matchers.level.max
    return True

def has_matcher(profile: Profile, campaign: Campaign) -> bool:
    matchers = campaign.matchers
    if matchers.has:
        if matchers.has.country:
            if profile.country not in matchers.has.country:
                return False
        if matchers.has.items:
            inventory_items = set(profile.inventory.keys())
            if not set(matchers.has.items).issubset(inventory_items):
                return False
    return True

def does_not_have_matcher(profile: Profile, campaign: Campaign) -> bool:
    matchers = campaign.matchers
    if matchers.does_not_have and matchers.does_not_have.items:
        for item, quantity in profile.inventory.items():
            if item in matchers.does_not_have.items and quantity > 0:
                return False
    return True

def match_campaign(profile: Profile, campaign: Campaign) -> bool:
    matcher_functions = [
        level_matcher,
        has_matcher,
        does_not_have_matcher
    ]
    return all(matcher(profile, campaign) for matcher in matcher_functions)
