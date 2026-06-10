from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_dashboard_overview_endpoint():
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "JARVIS-X"
    assert "voice_status" in data


def test_tools_list_endpoint():
    response = client.get("/api/tools/list")
    assert response.status_code == 200
    assert "tools" in response.json()
