from .tool_registry import ToolRegistry

class ToolExecutionLayer:
    def __init__(self):
        self.registry = ToolRegistry()

    def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {
                "status": "error",
                "tool_name": tool_name,
                "message": "Tool not found. Use /api/tools/list to see available tools."
            }
        return tool(parameters)

    def list_tools(self):
        return self.registry.list_tools()
