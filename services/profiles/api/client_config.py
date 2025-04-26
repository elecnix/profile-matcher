from fastapi import APIRouter, Depends, HTTPException
from services.profiles.service import ProfileService
from services.profiles.dependencies import get_service
from typing import Optional, Dict
import logging

router = APIRouter()

@router.get("/get_client_config/{player_id}")
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
            return profile.model_dump()
        raise HTTPException(status_code=404, detail="Profile not found")
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"get_client_config failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
