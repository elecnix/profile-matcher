"""
Unit tests for the ProfileRepository class.

This test file demonstrates how to isolate and test repository/database logic in a FastAPI project.
It uses AsyncMock to simulate MongoDB operations, so no real database is needed.

Key concepts:
- We create a fake database structure that mimics the real MongoDB collections.
- We use AsyncMock to mock async methods like find_one.
- This allows us to test only the repository logic, making our tests fast and reliable.
"""
import pytest
from hypothesis import given
from unittest.mock import AsyncMock
from services.profiles.repository.profiles import ProfileRepository
from services.profiles.repository.profiles_types import Profile
from hypothesis import strategies

profile_base_strategy = strategies.from_type(Profile)

def create_fake_db():
    return {
        "profiles_db": {
            "profiles": AsyncMock()
        }
    }

@pytest.mark.asyncio
@given(profile_base_strategy)
async def test_get_profile_by_player_id(expected_profile: Profile):
    fake_db = create_fake_db()
    fake_db["profiles_db"]["profiles"].find_one = AsyncMock(return_value=expected_profile.model_dump())
    repo = ProfileRepository(fake_db)
    result = await repo.get_profile_by_player_id(expected_profile.player_id)
    assert result.model_dump() == expected_profile.model_dump()
    assert "_id" not in result

@pytest.mark.asyncio
@given(profile_base_strategy.map(lambda p: p.model_copy(update={"_custom": "ok"})))
async def test_profile_custom_field_ok(profile: Profile):
    fake_db = create_fake_db()
    fake_db["profiles_db"]["profiles"].find_one = AsyncMock(return_value=profile.model_dump())
    repo = ProfileRepository(fake_db)
    result = await repo.get_profile_by_player_id(profile.player_id)
    assert result.model_dump() == profile.model_dump()
    assert "_custom" in result.model_dump(), "Profile should contain _custom field"

@pytest.mark.asyncio
@given(profile_base_strategy.map(lambda p: p.model_copy(update={"custom": "fail"})))
async def test_repository_rejects_profile_with_bad_custom_field(profile: Profile):
    fake_db = create_fake_db()
    fake_db["profiles_db"]["profiles"].find_one = AsyncMock(return_value=profile.model_dump())
    repo = ProfileRepository(fake_db)
    with pytest.raises(ValueError):
        await repo.get_profile_by_player_id(profile.player_id)
