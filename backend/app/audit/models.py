from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class AuditEvent(BaseModel):
    execution_id: str
    tenant_id: str
    event_type: str        # "user_message" | "intent" | "rag" | "plan" | "policy" | "tool_call" | "approval_request" | "approval_decision" | "final_response"
    payload: Dict[str, Any]
    timestamp: str


class ExecutionDetail(BaseModel):
    execution_id: str
    tenant_id: str
    events: List[AuditEvent]
    status: str            # "completed" | "pending_approval" | "rejected"
    pending_action: Optional[Dict[str, Any]] = None