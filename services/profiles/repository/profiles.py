from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient

class ProfileRepository:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def get_profile_by_player_id(self, player_id: str) -> Optional[Dict]:
        profile = await self.db["profiles_db"]["profiles"].find_one({"player_id": player_id})
        if profile:
            profile.pop("_id", None)
        return profile
