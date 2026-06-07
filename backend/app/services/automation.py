from typing import Any, Dict

from .memory import MemorySystem
from .tools import ToolExecutionLayer

class AutomationEngine:
    def __init__(self, tool_engine: ToolExecutionLayer, memory: MemorySystem):
        self.tool_engine = tool_engine
        self.memory = memory
        self.workflows: Dict[str, Dict[str, Any]] = {
            "system_check": {
                "description": "Run a local system check using available tools.",
                "steps": [
                    {"action": "tool", "tool": "system_info", "parameters": {}},
                    {"action": "tool", "tool": "list_files", "parameters": {"path": "."}},
                ],
            },
            "memory_audit": {
                "description": "Audit stored memory and return a summary.",
                "steps": [
                    {"action": "memory_summary"},
                ],
            },
            "tool_demo": {
                "description": "Run a quick tool demo to verify the tool layer.",
                "steps": [
                    {"action": "tool", "tool": "echo", "parameters": {"message": "JARVIS-X tool demo"}},
                    {"action": "tool", "tool": "system_info", "parameters": {}},
                ],
            },
        }

    def list_workflows(self) -> Dict[str, Any]:
        return {
            workflow_name: {"description": workflow["description"]}
            for workflow_name, workflow in self.workflows.items()
        }

    def run_workflow(self, workflow_name: str, parameters: dict) -> dict:
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {
                "status": "error",
                "workflow_name": workflow_name,
                "message": "Workflow not found. Use /api/automation/list to see available workflows."
            }

        results = []
        for step in workflow["steps"]:
            if step["action"] == "tool":
                execution = self.tool_engine.execute_tool(step["tool"], step.get("parameters", {}))
                results.append({"step": step, "result": execution})
            elif step["action"] == "memory_summary":
                items = self.memory.list_memory()
                results.append({
                    "step": step,
                    "result": {
                        "status": "success",
                        "memory_count": len(items),
                        "sample": items[:5]
                    }
                })
            else:
                results.append({"step": step, "result": {"status": "ignored", "message": "Unknown workflow action."}})

        return {
            "workflow_name": workflow_name,
            "status": "completed",
            "description": workflow["description"],
            "results": results,
            "parameters": parameters,
        }
