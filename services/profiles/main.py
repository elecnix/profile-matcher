import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import Optional, Dict

from services.profiles.repository.profile import ProfileRepository
from services.profiles.repository.campaign import CampaignRepository
from services.profiles.service import ProfileService

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    app.state.mongo_client = AsyncIOMotorClient(mongo_url)
    try:
        yield
    finally:
        app.state.mongo_client.close()

app = FastAPI(lifespan=lifespan)

def get_mongo_client() -> AsyncIOMotorClient:
    return app.state.mongo_client

# Dependency providers

def get_profile_repository(mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)) -> ProfileRepository:
    return ProfileRepository(mongo_client)

def get_campaign_repository() -> CampaignRepository:
    return CampaignRepository()

def get_service(
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    campaign_repository: CampaignRepository = Depends(get_campaign_repository),
) -> ProfileService:
    return ProfileService(profile_repository, campaign_repository)

# Endpoints

@app.get("/health")
async def health(mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)) -> Dict:
    """
    Check the health of the MongoDB database.
    """
    try:
        await mongo_client.admin.command({"ping": 1})
        return {"mongo": "ok"}
    except Exception as e:
        logging.error(f"MongoDB health check failed: {e}")
        return {"mongo": "unavailable", "error": str(e)}

@app.get("/get_client_config/{player_id}")
async def get_client_config(
    player_id: str,
    service: ProfileService = Depends(get_service)
) -> Optional[Dict]:
    """
    Get the client configuration for a specific player.
    """
    try:
        profile = await service.get_client_config(player_id)
        if profile:
            return profile
    except Exception as e:
        logging.error(f"get_client_config failed: {e}")
    raise HTTPException(status_code=404, detail="Profile not found")
