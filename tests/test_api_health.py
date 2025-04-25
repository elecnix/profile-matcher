"""
Integration tests for the /health FastAPI endpoint.
"""
from fastapi.testclient import TestClient
from services.profiles.main import app

def test_health_endpoint_success(monkeypatch):
    """
    Test the /health endpoint returns mongo: ok when ping succeeds.
    """
    class MockAdmin:
        async def command(self, cmd):
            return {"ok": 1}
    class MockMongo:
        @property
        def admin(self):
            return MockAdmin()
    def fake_get_mongo_client(request):
        return MockMongo()
    from services.profiles.api import health
    monkeypatch.setattr(health, "get_mongo_client", fake_get_mongo_client)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"mongo": "ok"}

def test_health_endpoint_failure(monkeypatch):
    """
    Test the /health endpoint returns mongo: unavailable when ping fails.
    """
    class MockAdmin:
        async def command(self, cmd):
            raise Exception("mock ping failed")
    class MockMongo:
        @property
        def admin(self):
            return MockAdmin()
    def fake_get_mongo_client(request):
        return MockMongo()
    from services.profiles.api import health
    monkeypatch.setattr(health, "get_mongo_client", fake_get_mongo_client)
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["mongo"] == "unavailable"
        assert "mock ping failed" in response.json()["error"]
