import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import boto3
from boto3.dynamodb.conditions import Key
from app.config import settings


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_dynamodb():
    return boto3.resource("dynamodb", region_name=settings.AWS_REGION)


def _get_audit_table():
    dynamodb = _get_dynamodb()
    return dynamodb.Table(settings.DYNAMO_AUDIT)


def _get_sessions_table():
    dynamodb = _get_dynamodb()
    return dynamodb.Table(settings.DYNAMO_SESSIONS)


def init_db() -> None:
    """No-op for DynamoDB as tables are pre-provisioned via IaC/CLI."""
    pass


def log_event(execution_id: str, tenant_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    """Log an audit event to DynamoDB table."""
    table = _get_audit_table()
    table.put_item(
        Item={
            "execution_id": execution_id,
            "timestamp": _now(),
            "tenant_id": tenant_id,
            "event_type": event_type,
            "payload": json.dumps(payload, default=str),
        }
    )


def create_execution(execution_id: str, tenant_id: str, status: str, pending_action: Optional[Dict[str, Any]] = None) -> None:
    """Create or update execution record in DynamoDB sessions/executions table."""
    table = _get_sessions_table()
    now = _now()
    item = {
        "session_id": execution_id,
        "tenant_id": tenant_id,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    if pending_action:
        item["pending_action"] = json.dumps(pending_action, default=str)
    table.put_item(Item=item)


def update_execution_status(execution_id: str, status: str, pending_action: Optional[Dict[str, Any]] = None) -> None:
    """Update execution status in DynamoDB."""
    table = _get_sessions_table()
    update_expr = "SET #st = :s, updated_at = :u"
    expr_attr_names = {"#st": "status"}
    expr_attr_values = {":s": status, ":u": _now()}
    if pending_action is not None:
        update_expr += ", pending_action = :p"
        expr_attr_values[":p"] = json.dumps(pending_action, default=str)
    
    table.update_item(
        Key={"session_id": execution_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
    )


def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve execution record and associated audit events."""
    sessions_table = _get_sessions_table()
    resp = sessions_table.get_item(Key={"session_id": execution_id})
    row = resp.get("Item")
    if not row:
        return None

    audit_table = _get_audit_table()
    events_resp = audit_table.query(
        KeyConditionExpression=Key("execution_id").eq(execution_id)
    )
    events = [
        {
            "execution_id": r["execution_id"],
            "tenant_id": r.get("tenant_id", row.get("tenant_id")),
            "event_type": r.get("event_type", ""),
            "payload": json.loads(r["payload"]) if isinstance(r.get("payload"), str) else r.get("payload", {}),
            "timestamp": r["timestamp"],
        }
        for r in events_resp.get("Items", [])
    ]
    events.sort(key=lambda x: x["timestamp"])

    pending_action = row.get("pending_action")
    if isinstance(pending_action, str):
        try:
            pending_action = json.loads(pending_action)
        except Exception:
            pass

    return {
        "execution_id": row["session_id"],
        "tenant_id": row.get("tenant_id", ""),
        "status": row.get("status", ""),
        "pending_action": pending_action,
        "events": events,
    }


def list_executions(tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """List executions for a given tenant from DynamoDB."""
    sessions_table = _get_sessions_table()
    resp = sessions_table.scan(Limit=limit)
    items = resp.get("Items", [])
    filtered = [
        {
            "execution_id": item["session_id"],
            "tenant_id": item.get("tenant_id", ""),
            "status": item.get("status", ""),
            "created_at": item.get("created_at", ""),
        }
        for item in items
        if item.get("tenant_id") == tenant_id or not tenant_id
    ]
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return filtered[:limit]


def get_audit_trail(execution_id: str) -> list:
    """Direct helper to query audit trail by execution_id."""
    audit_table = _get_audit_table()
    resp = audit_table.query(
        KeyConditionExpression=Key("execution_id").eq(execution_id)
    )
    items = resp.get("Items", [])
    items.sort(key=lambda x: x.get("timestamp", ""))
    return items
