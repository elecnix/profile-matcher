from typing import List
from services.profiles.repository.campaigns_types import Campaign
from services.profiles.repository.campaigns import CampaignRepository
from datetime import datetime, timedelta, timezone
import logging

class CampaignCache:
    def __init__(self, campaign_repository: CampaignRepository, refresh_seconds: int = 300, max_seconds: int = 3600):
        self._campaign_repository = campaign_repository
        self._refresh_seconds = refresh_seconds
        self._max_seconds = max_seconds
        self._campaign_cache = None
        self._campaign_cache_created_at = None

    async def get_currently_active_campaigns(self) -> List[Campaign]:
        """
        Get currently active campaigns, using the cache if not older than max_seconds, and attempting to refresh if older than refresh_seconds.
        """
        now = datetime.now(timezone.utc)
        campaigns = await self.get_upcoming_active_campaigns(now)
        return [c for c in campaigns if CampaignCache._campaign_is_active_now(c, now)]

    async def get_upcoming_active_campaigns(self, now: datetime) -> List[Campaign]:
        """
        Get upcoming active campaigns starting within the next max_seconds seconds.
        """

        # cache is younger than refresh_seconds? return as-is
        if self._campaign_cache is not None:
            cache_age = (now - self._campaign_cache_created_at)
            if cache_age < timedelta(seconds=self._refresh_seconds):
                # cache is fresh
                return self._campaign_cache
            elif cache_age < timedelta(seconds=self._max_seconds):
                # cache is stale, try to refresh
                try:
                    return await self._fetch_and_cache(now)
                except Exception as e:
                    logging.error(f"Error refreshing campaigns, using stale cache: {e}")
                    return self._campaign_cache
        return await self._fetch_and_cache(now)

    async def _fetch_and_cache(self, now: datetime) -> List[Campaign]:
        """
        Fetch and cache active campaigns starting within the next max_seconds seconds.
        """
        interval_end = now + timedelta(seconds=self._max_seconds)
        campaigns = await self._campaign_repository.get_active_campaigns(now, interval_end)
        self._campaign_cache = campaigns
        self._campaign_cache_created_at = now
        return campaigns

    @staticmethod
    def _campaign_is_active_now(campaign: Campaign, now: datetime) -> bool:
        """
        Check if a campaign is active at the given time.
        """
        try:
            start = datetime.fromisoformat(campaign.start_date)
            end = datetime.fromisoformat(campaign.end_date)
        except Exception as e:
            logging.warning(f"Invalid campaign dates: {campaign.start_date}, {campaign.end_date}: {e}")
            return False
        return start <= now <= end and campaign.enabled
