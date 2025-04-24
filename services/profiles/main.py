from fastapi import FastAPI
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

mongo_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    mongo_client = AsyncIOMotorClient(mongo_url)
    yield
    mongo_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    try:
        await mongo_client.admin.command({"ping": 1})
        return {"mongo": "ok"}
    except Exception as e:
        logging.error(f"MongoDB health check failed: {e}")
        return {"mongo": "unavailable", "error": str(e)}

@app.get("/get_client_config/{player_id}")
def get_client_config(player_id: str):
    # Placeholder: should call campaigns service, but returns empty for now
    return {}

@app.get("/profiles")
def get_profiles():
    # Placeholder for profile service
    return []
