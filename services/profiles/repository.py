from typing import Optional, List, Dict
from motor.motor_asyncio import AsyncIOMotorClient

import httpx

async def get_active_campaigns() -> List[Dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://campaigns:8000/campaigns")
        response.raise_for_status()
        return await response.json()

async def get_profile_by_player_id(db: AsyncIOMotorClient, player_id: str) -> Optional[Dict]:
    profile = await db["profiles_db"]["profiles"].find_one({"player_id": player_id})
    if profile:
        profile.pop("_id", None) # Hide internal MongoDB identifier from public interface
    return profile
