import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import Optional, Dict
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

from services.profiles.dependencies import get_service, get_mongo_client

@app.get("/health")
async def health(request: Request) -> Dict:
    """
    Check the health of the MongoDB database.
    """
    try:
        await get_mongo_client(request).admin.command({"ping": 1})
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
