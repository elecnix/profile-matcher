from typing import List, TypedDict
from pydantic import RootModel

from pydantic import BaseModel, RootModel
from typing import List, Optional

class LevelMatcher(BaseModel):
    min: int
    max: int

class HasMatcher(BaseModel):
    country: Optional[List[str]] = None
    items: Optional[List[str]] = None

class DoesNotHaveMatcher(BaseModel):
    items: Optional[List[str]] = None

class Matchers(BaseModel):
    level: Optional[LevelMatcher] = None
    has: Optional[HasMatcher] = None
    does_not_have: Optional[DoesNotHaveMatcher] = None

class Campaign(BaseModel):
    game: str
    name: str
    priority: float
    matchers: Matchers
    start_date: str
    end_date: str
    enabled: bool
    last_updated: str

class CampaignResponse(RootModel[List[Campaign]]):
    pass
