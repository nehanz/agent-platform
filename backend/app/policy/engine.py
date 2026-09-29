from typing import Dict, Any


REFUND_APPROVAL_THRESHOLD_USD = 100.0


def evaluate(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns:
      {"decision": "allow" | "require_approval" | "deny", "reason": str}
    """
    if tool_name == "create_refund":
        amount = float(tool_args.get("amount", 0))
        if amount <= 0:
            return {"decision": "deny", "reason": "Refund amount must be positive."}
        if amount > REFUND_APPROVAL_THRESHOLD_USD:
            return {
                "decision": "require_approval",
                "reason": f"Refund ${amount:.2f} exceeds ${REFUND_APPROVAL_THRESHOLD_USD:.0f} approval threshold.",
            }
        return {"decision": "allow", "reason": "Refund within auto-approval limit."}

    if tool_name == "check_order_status":
        return {"decision": "allow", "reason": "Read-only operation."}

    return {"decision": "deny", "reason": f"Unknown tool: {tool_name}"}