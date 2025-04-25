from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from .profiles_types import Profile

class ProfileRepository:
    """
    Repository class for accessing player profile data in MongoDB.

    This class provides methods to interact with the profiles collection in the database.
    It abstracts the database logic away from the business logic, making the code more modular and testable.

    Args:
        db (AsyncIOMotorClient): The MongoDB client or a mock/fake object for testing.

    Usage:
        repo = ProfileRepository(db)
        profile = await repo.get_profile_by_player_id("some_player_id")
    """
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def get_profile_by_player_id(self, player_id: str) -> Optional[Profile]:
        profile = await self.db["profiles_db"]["profiles"].find_one({"player_id": player_id})
        if profile:
            profile.pop("_id", None)
        return profile
