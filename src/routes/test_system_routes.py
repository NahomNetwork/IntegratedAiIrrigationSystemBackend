import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_purge_sensordata_by_date_invalid_date():
    # Invalid date format should return 400
    response = client.get("/system/sensordata/purge-by-date?start_date=bad-date&end_date=2025-05-24")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]

def test_purge_sensordata_by_date_success(monkeypatch):
    # Mock DB actions for testing success flow
    async def mock_execute(*args, **kwargs): pass
    async def mock_commit(): pass
    class MockDB:
        async def execute(self, *a, **k): await mock_execute()
        async def commit(self): await mock_commit()
    # Dependency override
    app.dependency_overrides = {}
    from src.routes.system_routes import get_db
    app.dependency_overrides[get_db] = lambda: MockDB()
    response = client.get("/system/sensordata/purge-by-date?start_date=2025-05-17&end_date=2025-05-24")
    assert response.status_code == 200
    assert response.json()["message"] == "Sensor data purged successfully"