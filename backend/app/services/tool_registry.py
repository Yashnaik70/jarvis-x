import platform
from typing import Any, Dict, Callable, List
import requests
from ..core.config import settings

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "echo": self.echo,
            "system_info": self.system_info,
            "read_file": self.read_file,
            "list_files": self.list_files,
            "find_in_file": self.find_in_file,
            "search_web": self.search_web,
        }

    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)

    def echo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        message = parameters.get("message", "")
        return {"status": "success", "echo": message}

    def system_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "python_version": platform.python_version(),
        }

    def read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        path = parameters.get("path")
        if not path:
            return {"status": "error", "message": "Missing path parameter."}
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return {"status": "error", "message": "File not found."}
        if os.path.isdir(abs_path):
            return {"status": "error", "message": "Path is a directory, not a file."}
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2048)
            return {"status": "success", "file": abs_path, "content": content}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def list_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        path = parameters.get("path", ".")
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return {"status": "error", "message": "Path not found."}
        try:
            entries = os.listdir(abs_path)
            return {"status": "success", "path": abs_path, "entries": entries}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def find_in_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        path = parameters.get("path")
        query = parameters.get("query")
        if not path or not query:
            return {"status": "error", "message": "Missing path or query parameter."}
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path) or os.path.isdir(abs_path):
            return {"status": "error", "message": "File not found or invalid."}
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            hits = [line for line in content.splitlines() if query.lower() in line.lower()]
            return {"status": "success", "path": abs_path, "query": query, "hits": hits[:20]}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def search_web(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        query = parameters.get("query")
        if not query:
            return {"status": "error", "message": "Missing query parameter."}
        if not settings.serpapi_key:
            return {"status": "error", "message": "SERPAPI_KEY not set in environment."}

        try:
            url = "https://serpapi.com/search.json"
            params = {"q": query, "api_key": settings.serpapi_key}
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return {"status": "error", "message": f"Search API error: {resp.status_code}", "details": resp.text}
            data = resp.json()
            organic = data.get("organic_results") or data.get("organic") or []
            results = []
            for r in organic[:8]:
                results.append({
                    "title": r.get("title") or r.get("position"),
                    "link": r.get("link") or r.get("url"),
                    "snippet": r.get("snippet") or r.get("snippet_text")
                })
            return {"status": "success", "query": query, "results": results}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
