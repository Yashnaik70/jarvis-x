from pydantic import BaseModel
from typing import Any, Dict

class CommandRequest(BaseModel):
    command: str

class VoiceCommandRequest(BaseModel):
    command: str

class VoiceTranscribeRequest(BaseModel):
    audio_base64: str

class VoiceTTSRequest(BaseModel):
    text: str
    lang: str = "en"

class MemoryAddRequest(BaseModel):
    key: str
    value: str

class MemoryQueryRequest(BaseModel):
    key: str

class AgentExecuteRequest(BaseModel):
    agent_name: str
    payload: Dict[str, Any] = {}

class AutomationRequest(BaseModel):
    workflow_name: str
    parameters: Dict[str, Any] = {}

class ToolExecuteRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}
    approval_id: str | None = None

class ApprovalRequest(BaseModel):
    action: str
    details: str

class ApprovalDecisionRequest(BaseModel):
    approval_id: str
    decision: str
