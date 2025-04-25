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
from unittest.mock import AsyncMock
from services.profiles.repository.profiles import ProfileRepository

@pytest.mark.asyncio
async def test_get_profile_by_player_id():
    """
    Test that get_profile_by_player_id returns the correct profile from the database.

    This test mocks the database and the find_one method to control the output.
    It verifies that the repository method returns the expected profile and removes the '_id' field.
    """
    # Given
    fake_db = {
        "profiles_db": {
            "profiles": AsyncMock() # the result of a call is an awaitable
        }
    }
    expected_profile = {"player_id": "123", "name": "Test"}
    fake_db["profiles_db"]["profiles"].find_one = AsyncMock(return_value=expected_profile) # return value when awaited
    repo = ProfileRepository(fake_db)
    # When
    result = await repo.get_profile_by_player_id("123")
    # Then
    assert result == expected_profile
    assert "_id" not in result
