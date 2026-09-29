from typing import Dict, Any


# Mock order database — keyed by order_id, scoped by tenant
_MOCK_ORDERS = {
    ("tenantA", "ORD-1001"): {"status": "delivered", "amount": 45.00, "customer": "alice@example.com"},
    ("tenantA", "ORD-1002"): {"status": "shipped",   "amount": 180.00, "customer": "bob@example.com"},
    ("tenantA", "ORD-1003"): {"status": "delivered", "amount": 220.00, "customer": "carol@example.com"},
    ("tenantB", "ORD-2001"): {"status": "processing", "amount": 60.00, "customer": "dave@example.com"},
}


def check_order_status(order_id: str, tenant_id: str) -> Dict[str, Any]:
    order = _MOCK_ORDERS.get((tenant_id, order_id))
    if not order:
        return {"ok": False, "error": f"Order {order_id} not found for tenant {tenant_id}"}
    return {
        "ok": True,
        "order_id": order_id,
        "status": order["status"],
        "amount": order["amount"],
        "customer": order["customer"],
    }