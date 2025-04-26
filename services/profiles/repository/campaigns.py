from typing import List, Optional
from .campaigns_types import Campaign, CampaignResponse
import httpx
from datetime import datetime, timezone
from aiocache import cached, SimpleMemoryCache

class CampaignRepository:
    async def get_active_campaigns(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Campaign]:
        """
        Get active campaigns in the given interval. If no interval is given, active campaigns at the current time are returned.
        """
        now = datetime.now(timezone.utc)
        if not start_date:
            start_date = now
        if not end_date:
            end_date = now
        return await self._fetch_campaigns(start_date, end_date)

    @cached(ttl=300, cache=SimpleMemoryCache)
    async def _fetch_campaigns(self, start_date: datetime, end_date: datetime) -> List[Campaign]:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://campaigns:8000/campaigns", params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()})
            response.raise_for_status()
            campaigns_raw = response.json()
            campaigns_response = CampaignResponse(campaigns_raw)
            return campaigns_response.root # validated list of Campaign models
