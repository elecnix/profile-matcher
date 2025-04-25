from typing import List, Dict
from pydantic import BaseModel, model_validator

class Device(BaseModel):
    id: int
    model: str
    carrier: str
    firmware: str

# Inventory is a mapping of item name to quantity
Inventory = Dict[str, int]

class Clan(BaseModel):
    id: str
    name: str

class Profile(BaseModel, extra='allow'):
    player_id: str
    credential: str
    created: str
    modified: str
    last_session: str
    total_spent: int
    total_refund: int
    total_transactions: int
    last_purchase: str
    active_campaigns: List[str]
    devices: List[Device]
    level: int
    xp: int
    total_playtime: int
    country: str
    language: str
    birthdate: str
    gender: str
    inventory: Inventory
    clan: Clan

    @model_validator(mode="before")
    @classmethod
    def check_custom_fields(cls, values: dict) -> dict:
        known_fields = set(cls.model_fields)
        for key in values:
            if key not in known_fields and not key.startswith("_"):
                raise ValueError(f"Custom profile field '{key}' must start with '_' (got: {key})")
        return values
