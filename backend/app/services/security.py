import uuid
from typing import Dict, Any

class ApprovalSystem:
    def __init__(self):
        self.requests: Dict[str, Dict[str, Any]] = {}

    def request_approval(self, action: str, details: str) -> Dict[str, Any]:
        approval_id = str(uuid.uuid4())
        self.requests[approval_id] = {
            "approval_id": approval_id,
            "action": action,
            "details": details,
            "status": "pending",
            "decision": None
        }
        return self.requests[approval_id]

    def get_status(self, approval_id: str) -> Dict[str, Any]:
        request = self.requests.get(approval_id)
        if not request:
            raise KeyError("Approval request not found")
        return request

    def decide(self, approval_id: str, decision: str) -> Dict[str, Any]:
        if approval_id not in self.requests:
            raise KeyError("Approval request not found")
        if decision not in {"approved", "denied"}:
            raise ValueError("Decision must be 'approved' or 'denied'")
        self.requests[approval_id]["status"] = decision
        self.requests[approval_id]["decision"] = decision
        return self.requests[approval_id]

    def list_requests(self) -> Dict[str, Dict[str, Any]]:
        return self.requests
