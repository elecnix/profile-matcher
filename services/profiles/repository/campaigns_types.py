from typing import TypedDict, List

class LevelMatcher(TypedDict):
    min: int
    max: int

class HasMatcher(TypedDict, total=False):
    country: List[str]
    items: List[str]

class DoesNotHaveMatcher(TypedDict, total=False):
    items: List[str]

class Matchers(TypedDict, total=False):
    level: LevelMatcher
    has: HasMatcher
    does_not_have: DoesNotHaveMatcher

class Campaign(TypedDict):
    game: str
    name: str
    priority: float
    matchers: Matchers
    start_date: str
    end_date: str
    enabled: bool
    last_updated: str
