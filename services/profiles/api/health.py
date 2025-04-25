from fastapi import APIRouter, Request
from services.profiles.dependencies import get_mongo_client
import logging

router = APIRouter()

@router.get("/health")
async def health(request: Request):
    """
    Check the health of the MongoDB database.
    """
    try:
        await get_mongo_client(request).admin.command({"ping": 1})
        return {"mongo": "ok"}
    except Exception as e:
        logging.error(f"MongoDB health check failed: {e}")
        return {"mongo": "unavailable", "error": str(e)}
