from typing import List, Dict
import httpx

class CampaignRepository:
    async def get_active_campaigns(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://campaigns:8000/campaigns")
            response.raise_for_status()
            return await response.json()
