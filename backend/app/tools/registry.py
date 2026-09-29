from typing import Dict, Any, Callable
from .check_order_status import check_order_status
from .create_refund import create_refund


TOOLS: Dict[str, Dict[str, Any]] = {
    "check_order_status": {
        "fn": check_order_status,
        "schema": {
            "name": "check_order_status",
            "description": "Check the current status of a customer order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID, e.g. ORD-1001"},
                },
                "required": ["order_id"],
            },
        },
    },
    "create_refund": {
        "fn": create_refund,
        "schema": {
            "name": "create_refund",
            "description": "Create a refund for an order. Refunds over $100 require human approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "amount": {"type": "number", "description": "Refund amount in USD"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "amount", "reason"],
            },
        },
    },
}


def execute_tool(tool_name: str, tool_args: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    if tool_name not in TOOLS:
        return {"ok": False, "error": f"Unknown tool: {tool_name}"}
    args = dict(tool_args)
    args["tenant_id"] = tenant_id  # enforce tenant isolation at the tool boundary
    try:
        return TOOLS[tool_name]["fn"](**args)
    except TypeError as e:
        return {"ok": False, "error": f"Invalid arguments for {tool_name}: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"Tool execution failed: {e}"}