import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    app.state.mongo_client = AsyncIOMotorClient(mongo_url)
    try:
        yield
    finally:
        app.state.mongo_client.close()

app = FastAPI(lifespan=lifespan)

def get_mongo_client():
    return app.state.mongo_client

@app.get("/health")
async def health(mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    try:
        await mongo_client.admin.command({"ping": 1})
        return {"mongo": "ok"}
    except Exception as e:
        logging.error(f"MongoDB health check failed: {e}")
        return {"mongo": "unavailable", "error": str(e)}

@app.get("/get_client_config/{player_id}")
async def get_client_config(player_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    profile = await mongo_client["profiles_db"]["profiles"].find_one({"player_id": player_id})
    if profile:
        profile.pop("_id", None)  # Remove _id field if present
        return profile
    raise HTTPException(status_code=404, detail="Profile not found")
