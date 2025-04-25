from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from services.profiles.repository.campaigns_cache import CampaignCache
from services.profiles.repository.profiles import ProfileRepository
from services.profiles.repository.campaigns import CampaignRepository
from services.profiles.service import ProfileService
from fastapi import Request

def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    return request.app.state.mongo_client

def get_profile_repository(mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)) -> ProfileRepository:
    return ProfileRepository(mongo_client)

def get_campaign_repository() -> CampaignRepository:
    return CampaignRepository()

def get_service(
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    campaign_repository: CampaignRepository = Depends(get_campaign_repository),
) -> ProfileService:
    return ProfileService(profile_repository, campaign_repository, CampaignCache)
