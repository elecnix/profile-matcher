from typing import TypedDict, List, Dict, Optional

class Device(TypedDict):
    id: int
    model: str
    carrier: str
    firmware: str

# Inventory is a mapping of item name to quantity
Inventory = Dict[str, int]

class Clan(TypedDict):
    id: str
    name: str

class Profile(TypedDict, total=False):
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
