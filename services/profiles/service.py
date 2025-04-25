
from services.profiles.repository import get_profile_by_player_id
from services.profiles.repository import get_active_campaigns
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient


async def get_client_config(db: AsyncIOMotorClient, player_id: str) -> Optional[Dict]:
    profile = await get_profile_by_player_id(db, player_id)
    if profile:
        active_campaigns = await get_active_campaigns()
        profile["active_campaigns"] = active_campaigns
    return profile
