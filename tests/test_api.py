from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Enterprise AI Research Agent" in data["service"]


def test_research_async_submission():
    response = client.post("/research", json={"query": "Test query for unit test", "max_rounds": 1})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "queued"
    assert data["user_query"] == "Test query for unit test"

