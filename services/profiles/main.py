import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import Optional, Dict
from services.profiles.api import health_router, client_config_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    app.state.mongo_client = AsyncIOMotorClient(mongo_url)
    try:
        yield
    finally:
        app.state.mongo_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(client_config_router)
