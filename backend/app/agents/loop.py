import json
import re
import uuid
from typing import Dict, Any, Optional

from app.llm import get_llm_provider
from app.rag import retrieve
from app.tools import execute_tool, TOOLS
from app.policy import evaluate
from app.audit import log_event, create_execution, update_execution_status, get_execution
from app.notify import send_approval_request
from .prompts import SYSTEM_PROMPT


def _extract_json(text: str) -> Dict[str, Any]:
    """Robustly pull a JSON object out of LLM output."""
    text = text.strip()
    # Strip markdown fences if model added them
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: grab first {...} block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _build_user_prompt(user_message: str, rag_chunks, history) -> str:
    ctx_lines = []
    for i, c in enumerate(rag_chunks, 1):
        ctx_lines.append(f"[{i}] ({c['source']}, tenant={c['tenant_id']}) {c['text']}")
    ctx_block = "\n".join(ctx_lines) if ctx_lines else "(no relevant context found)"

    hist_lines = []
    for m in history[-6:]:
        hist_lines.append(f"{m['role']}: {m['content']}")
    hist_block = "\n".join(hist_lines) if hist_lines else "(none)"

    tool_list = "\n".join(
        f"- {name}: {spec['schema']['description']}" for name, spec in TOOLS.items()
    )

    return f"""Available tools:
{tool_list}

Retrieved knowledge base context:
{ctx_block}

Conversation history:
{hist_block}

User message:
{user_message}
"""


def run_agent(user_message: str, tenant_id: str, history: Optional[list] = None) -> Dict[str, Any]:
    history = history or []
    execution_id = f"exec-{uuid.uuid4().hex[:12]}"
    create_execution(execution_id, tenant_id, status="running")
    log_event(execution_id, tenant_id, "user_message", {"content": user_message})

    llm = get_llm_provider()

    # Step 1: RAG retrieval (also gives intent classifier context)
    rag_chunks = retrieve(user_message, tenant_id=tenant_id, top_k=3)
    log_event(execution_id, tenant_id, "rag", {"chunks": rag_chunks})

    # Step 2: LLM plan
    user_prompt = _build_user_prompt(user_message, rag_chunks, history)
    raw = llm.chat(messages=[{"role": "user", "content": user_prompt}], system=SYSTEM_PROMPT)

    try:
        parsed = _extract_json(raw)
    except Exception as e:
        log_event(execution_id, tenant_id, "plan_error", {"raw": raw, "error": str(e)})
        update_execution_status(execution_id, "completed")
        return {
            "execution_id": execution_id,
            "status": "completed",
            "response": "I couldn't process that request. Please try rephrasing.",
        }

    log_event(execution_id, tenant_id, "plan", parsed)

    intent = parsed.get("intent", "other")
    plan = parsed.get("plan") or {}
    tool_name = plan.get("tool_name")
    tool_args = plan.get("tool_args") or {}
    response_text = parsed.get("response_text", "")

    # Step 3: No tool → straight response
    if not tool_name:
        log_event(execution_id, tenant_id, "final_response", {"text": response_text})
        update_execution_status(execution_id, "completed")
        return {
            "execution_id": execution_id,
            "status": "completed",
            "intent": intent,
            "response": response_text,
        }

    # Step 4: Policy check
    decision = evaluate(tool_name, tool_args)
    log_event(execution_id, tenant_id, "policy", {"tool": tool_name, "args": tool_args, "decision": decision})

    if decision["decision"] == "deny":
        update_execution_status(execution_id, "completed")
        return {
            "execution_id": execution_id,
            "status": "denied",
            "intent": intent,
            "response": f"I cannot perform that action: {decision['reason']}",
        }

    if decision["decision"] == "require_approval":
        pending = {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "reason": decision["reason"],
        }
        update_execution_status(execution_id, "pending_approval", pending)
        log_event(execution_id, tenant_id, "approval_request", pending)
        try:
            send_approval_request(execution_id, tool_name, tool_args, tenant_id)
        except Exception as e:
            log_event(execution_id, tenant_id, "sns_notify_error", {"error": str(e)})
        return {
            "execution_id": execution_id,
            "status": "pending_approval",
            "intent": intent,
            "pending_action": pending,
            "response": (
                f"This action requires human approval: {decision['reason']} "
                f"Requested: {tool_name}({tool_args})."
            ),
        }

    # Step 5: Auto-approved → execute tool
    result = execute_tool(tool_name, tool_args, tenant_id)
    log_event(execution_id, tenant_id, "tool_call", {"tool": tool_name, "args": tool_args, "result": result})

    final_text = _compose_final_response(llm, user_message, tool_name, result, response_text)
    log_event(execution_id, tenant_id, "final_response", {"text": final_text})
    update_execution_status(execution_id, "completed")

    return {
        "execution_id": execution_id,
        "status": "completed",
        "intent": intent,
        "tool_result": result,
        "response": final_text,
    }


def _compose_final_response(llm, user_message, tool_name, tool_result, draft_text) -> str:
    followup = f"""You previously planned a tool call.

User: {user_message}
Tool: {tool_name}
Tool result: {json.dumps(tool_result, default=str)}

Write a concise, friendly 1-2 sentence reply for the user based on the tool result.
Do NOT output JSON. Plain text only."""

    try:
        return llm.chat(messages=[{"role": "user", "content": followup}]).strip()
    except Exception:
        return draft_text or f"Done. Tool {tool_name} returned: {tool_result}"


def resume_after_approval(execution_id: str, approved: bool, approver: str) -> Dict[str, Any]:
    record = get_execution(execution_id)
    if not record:
        return {"ok": False, "error": "execution not found"}

    if record["status"] != "pending_approval":
        return {"ok": False, "error": f"execution is not pending approval (status={record['status']})"}

    pending = record["pending_action"]
    tenant_id = record["tenant_id"]

    log_event(execution_id, tenant_id, "approval_decision", {"approved": approved, "approver": approver})

    if not approved:
        update_execution_status(execution_id, "rejected")
        return {
            "ok": True,
            "execution_id": execution_id,
            "status": "rejected",
            "response": f"Action rejected by {approver}.",
        }

    result = execute_tool(pending["tool_name"], pending["tool_args"], tenant_id)
    log_event(execution_id, tenant_id, "tool_call", {
        "tool": pending["tool_name"],
        "args": pending["tool_args"],
        "result": result,
        "after_approval": True,
    })

    llm = get_llm_provider()
    final_text = _compose_final_response(
        llm,
        f"(post-approval) {pending['tool_name']}",
        pending["tool_name"],
        result,
        draft_text="",
    )
    log_event(execution_id, tenant_id, "final_response", {"text": final_text})
    update_execution_status(execution_id, "completed")

    return {
        "ok": True,
        "execution_id": execution_id,
        "status": "completed",
        "tool_result": result,
        "response": final_text,
    }