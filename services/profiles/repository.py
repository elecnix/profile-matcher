from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

async def get_profile_by_player_id(db: AsyncIOMotorClient, player_id: str) -> Optional[dict]:
    profile = await db["profiles_db"]["profiles"].find_one({"player_id": player_id})
    if profile:
        profile.pop("_id", None) # Hide internal MongoDB identifier from public interface
    return profile
