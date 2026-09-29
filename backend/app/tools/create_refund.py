from typing import Dict, Any
import uuid
from datetime import datetime, timezone

# In-memory refund store for local dev
_REFUNDS = []


def create_refund(order_id: str, amount: float, reason: str, tenant_id: str) -> Dict[str, Any]:
    refund_id = f"RFD-{uuid.uuid4().hex[:8].upper()}"
    record = {
        "refund_id": refund_id,
        "order_id": order_id,
        "amount": float(amount),
        "reason": reason,
        "tenant_id": tenant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "processed",
    }
    _REFUNDS.append(record)
    return {"ok": True, **record}