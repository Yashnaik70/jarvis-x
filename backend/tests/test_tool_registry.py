from backend.app.core.config import settings
from backend.app.services.tool_registry import ToolRegistry


def test_search_web_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "serpapi_key", "")
    result = ToolRegistry().search_web({"query": "py"})
    assert result["status"] == "error"
    assert "SERPAPI_KEY" in result["message"]


def test_search_web_missing_query():
    result = ToolRegistry().search_web({})
    assert result["status"] == "error"
    assert "Missing query" in result["message"]
