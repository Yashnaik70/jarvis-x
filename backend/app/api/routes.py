from fastapi import APIRouter, HTTPException, Depends, Header, status
from ..core.config import settings
from ..models import (
    AgentExecuteRequest,
    ApprovalDecisionRequest,
    ApprovalRequest,
    AutomationRequest,
    CommandRequest,
    MemoryAddRequest,
    MemoryQueryRequest,
    ToolExecuteRequest,
    VoiceCommandRequest,
    VoiceTranscribeRequest,
    VoiceTTSRequest,
)
from ..services.agents import AgentSystem
from ..services.automation import AutomationEngine
from ..services.brain import AIBrain
from ..services.memory import MemorySystem
from ..services.security import ApprovalSystem
from ..services.tools import ToolExecutionLayer
from ..services.voice import VoiceSystem

def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None, alias="Authorization")
):
    if not settings.jarvisx_api_key or settings.jarvisx_api_key.strip().lower().startswith("your_"):
        return
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key
    if token != settings.jarvisx_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"}
        )

router = APIRouter(prefix="/api", dependencies=[Depends(verify_api_key)])

memory = MemorySystem()
agents = AgentSystem()
voice = VoiceSystem()
brain = AIBrain(memory, agents, voice)
tool_engine = ToolExecutionLayer()
memory = MemorySystem()
automation_engine = AutomationEngine(tool_engine, memory)
approval_system = ApprovalSystem()

destructive_tools = {
    "delete_file",
    "move_file",
    "rename_file",
    "execute_script",
    "delete_memory",
    "shutdown_system"
}


def register_default_agents():
    agents.register_agent("research", lambda payload: {
        "agent": "research",
        "status": "ready",
        "result": "Research agent is prepared. Web search integration is pending."
    })
    agents.register_agent("knowledge", lambda payload: {
        "agent": "knowledge",
        "status": "ready",
        "result": "Knowledge agent is prepared. Memory organization is pending."
    })
    agents.register_agent("automation", lambda payload: {
        "agent": "automation",
        "status": "ready",
        "result": "Automation agent is prepared. Workflow execution is pending."
    })

register_default_agents()


@router.get("/info")
async def get_info():
    return {
        "name": "JARVIS-X",
        "description": "Modular AI assistant platform",
        "components": ["voice", "memory", "agents", "tools", "automation"]
    }


@router.post("/brain/command")
async def process_command(request: CommandRequest):
    return brain.process_command(request.command)


@router.post("/brain/execute")
async def execute_brain_command(request: CommandRequest):
    result = brain.process_command(request.command)
    if result.get("action") == "tool":
        execution = tool_engine.execute_tool(result.get("tool"), result.get("parameters", {}))
        return {
            "action": "tool_execution",
            "brain_result": result,
            "tool_result": execution
        }
    return {"action": result.get("action"), "result": result}


@router.post("/memory/add")
async def memory_add(request: MemoryAddRequest):
    memory.add_memory(request.key, request.value)
    return {"status": "stored", "key": request.key, "value": request.value}


@router.post("/memory/query")
async def memory_query(request: MemoryQueryRequest):
    value = memory.retrieve_memory(request.key)
    if value is None:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return {"key": request.key, "value": value}


@router.get("/memory/search")
async def memory_search(q: str):
    results = memory.search_memory(q)
    return [{"key": key, "value": value, "created_at": created_at} for key, value, created_at in results]


@router.get("/memory/list")
async def memory_list():
    items = memory.list_memory()
    return [{"key": key, "value": value, "created_at": created_at} for key, value, created_at in items]


@router.get("/voice/status")
async def voice_status():
    return voice.get_status()


@router.post("/voice/command")
async def voice_command(request: VoiceCommandRequest):
    parsed = voice.interpret_command(request.command)
    result = brain.process_command(parsed)
    if result.get("action") == "tool":
        execution = tool_engine.execute_tool(result.get("tool"), result.get("parameters", {}))
        return {
            "status": "received",
            "command": parsed,
            "brain_result": result,
            "tool_result": execution
        }
    return {"status": "received", "command": parsed, "result": result}


@router.post("/voice/transcribe")
async def voice_transcribe(request: VoiceTranscribeRequest):
    return voice.transcribe_audio(request.audio_base64)


@router.post("/voice/tts")
async def voice_tts(request: VoiceTTSRequest):
    return voice.generate_speech(request.text, request.lang)


@router.get("/dashboard/overview")
async def dashboard_overview():
    memory_items = memory.list_memory()
    return {
        "system": "JARVIS-X",
        "voice_status": voice.get_status(),
        "agents": list(agents.agents.keys()),
        "agent_count": len(agents.agents),
        "memory_count": len(memory_items),
        "health": "healthy"
    }


@router.get("/agents/list")
async def agents_list():
    return {"agents": agents.list_agents()}


@router.post("/agent/execute")
async def execute_agent(request: AgentExecuteRequest):
    try:
        result = agents.execute_agent(request.agent_name, request.payload)
        return {"status": "executed", "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/tool/execute")
async def execute_tool(request: ToolExecuteRequest):
    if request.tool_name in destructive_tools and not request.approval_id:
        approval = approval_system.request_approval(
            action="tool_execution",
            details=f"Execution of destructive tool: {request.tool_name} with parameters {request.parameters}"
        )
        return {
            "status": "approval_required",
            "approval_id": approval["approval_id"],
            "message": "This tool requires approval before execution. Use /api/approval/decision to approve or deny."
        }

    if request.tool_name in destructive_tools and request.approval_id:
        approval_status = approval_system.get_status(request.approval_id)
        if approval_status["status"] != "approved":
            return {
                "status": "denied",
                "message": "Tool execution denied until approval is granted."
            }

    return tool_engine.execute_tool(request.tool_name, request.parameters)


@router.get("/tools/list")
async def tools_list():
    available_tools = tool_engine.list_tools()
    return {"tools": available_tools}


@router.get("/approval/list")
async def approval_list():
    return {"approvals": approval_system.list_requests()}


@router.post("/approval/request")
async def approval_request(request: ApprovalRequest):
    approval = approval_system.request_approval(request.action, request.details)
    return {"status": "pending", "approval_id": approval["approval_id"], "details": approval["details"]}


@router.get("/approval/status/{approval_id}")
async def approval_status(approval_id: str):
    try:
        status = approval_system.get_status(approval_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found")


@router.post("/approval/decision")
async def approval_decision(request: ApprovalDecisionRequest):
    try:
        decision = approval_system.decide(request.approval_id, request.decision)
        return decision
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval request not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/automation/list")
async def automation_list():
    return {"workflows": automation_engine.list_workflows()}


@router.post("/automation/run")
async def run_workflow(request: AutomationRequest):
    return automation_engine.run_workflow(request.workflow_name, request.parameters)
