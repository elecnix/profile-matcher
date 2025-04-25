from typing import Optional, Dict
from services.profiles.repository.campaigns_types import Campaign
from services.profiles.repository.profiles_types import Profile
from services.profiles.repository.profiles import ProfileRepository
from services.profiles.repository.campaigns import CampaignRepository

class ProfileService:
    def __init__(self, profile_repository: ProfileRepository, campaign_repository: CampaignRepository):
        self.profile_repository = profile_repository
        self.campaign_repository = campaign_repository

    async def get_client_config(self, player_id: str) -> Optional[Profile]:
        profile = await self.profile_repository.get_profile_by_player_id(player_id)
        if not profile:
            return None
        campaigns = await self.campaign_repository.get_active_campaigns()
        matched_campaigns = []
        for campaign in campaigns:
            if match_campaign(profile, campaign):
                matched_campaigns.append(campaign.name)
        profile.active_campaigns = matched_campaigns
        return profile

def match_campaign(profile: Profile, campaign: Campaign) -> bool:
    matchers = campaign.matchers
    # Level matcher
    if matchers.level:
        if not (matchers.level.min <= profile.level <= matchers.level.max):
            return False
    # Has matcher
    if matchers.has:
        if matchers.has.country:
            if profile.country not in matchers.has.country:
                return False
        if matchers.has.items:
            inventory_items = set(profile.inventory.keys())
            if not set(matchers.has.items).issubset(inventory_items):
                return False
    # DoesNotHave matcher
    if matchers.does_not_have and matchers.does_not_have.items:
        inventory_items = set(profile.inventory.keys())
        if set(matchers.does_not_have.items) & inventory_items:
            return False
    return True
