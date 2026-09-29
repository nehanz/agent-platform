from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.auth import get_current_tenant
from app.agents import run_agent, resume_after_approval
from app.audit import get_execution, list_executions

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class ApproveRequest(BaseModel):
    execution_id: str
    approved: bool
    approver: Optional[str] = "demo-approver"


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_tenant)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")
    result = run_agent(req.message, tenant_id=user["tenant_id"], history=req.history)
    return result


@router.post("/approve")
def approve(req: ApproveRequest, user=Depends(get_current_tenant)):
    result = resume_after_approval(req.execution_id, req.approved, req.approver or user["email"])
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "approval failed"))
    return result


@router.get("/audit/{execution_id}")
def audit(execution_id: str, user=Depends(get_current_tenant)):
    record = get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="execution not found")
    if record["tenant_id"] != user["tenant_id"]:
        raise HTTPException(status_code=403, detail="not authorized for this execution")
    return record


@router.get("/audit")
def audit_list(user=Depends(get_current_tenant)):
    return {"executions": list_executions(user["tenant_id"])}