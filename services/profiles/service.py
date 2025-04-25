from typing import Optional, Dict
from services.profiles.repository.profile import ProfileRepository
from services.profiles.repository.campaign import CampaignRepository

class ProfileService:
    def __init__(self, profile_repository: ProfileRepository, campaign_repository: CampaignRepository):
        self.profile_repository = profile_repository
        self.campaign_repository = campaign_repository

    async def get_client_config(self, player_id: str) -> Optional[Dict]:
        profile = await self.profile_repository.get_profile_by_player_id(player_id)
        if profile:
            active_campaigns = await self.campaign_repository.get_active_campaigns()
            profile["active_campaigns"] = active_campaigns
        return profile
