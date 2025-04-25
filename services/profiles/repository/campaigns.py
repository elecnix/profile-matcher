from typing import List
from .campaigns_types import Campaign
import httpx

class CampaignRepository:
    async def get_active_campaigns(self) -> List[Campaign]:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://campaigns:8000/campaigns")
            response.raise_for_status()
            return await response.json()
