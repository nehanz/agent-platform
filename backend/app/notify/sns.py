import json
import os
from typing import Any, Dict, Optional
import boto3
from app.config import settings


def _get_sns_client():
    return boto3.client("sns", region_name=settings.AWS_REGION)


def send_approval_request(execution_id: str, tool: str, args: Dict[str, Any], tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """Send an SNS notification requesting human approval for high-risk actions (e.g. refunds > $100)."""
    if not settings.SNS_ARN:
        return {"status": "skipped", "reason": "SNS_ARN not configured"}

    sns = _get_sns_client()
    formatted_args = json.dumps(args, indent=2)
    message = (
        f"🚨 [Agent Approval Required]\n\n"
        f"Execution ID: {execution_id}\n"
        f"Tenant ID: {tenant_id or 'default'}\n"
        f"Tool Requested: {tool}\n"
        f"Arguments:\n{formatted_args}\n\n"
        f"Please verify this action before confirming."
    )
    
    resp = sns.publish(
        TopicArn=settings.SNS_ARN,
        Subject=f"Approval Request: {tool} ({execution_id[:8]})",
        Message=message,
        MessageAttributes={
            "execution_id": {"DataType": "String", "StringValue": execution_id},
            "tool": {"DataType": "String", "StringValue": tool},
        }
    )
    return {"status": "sent", "message_id": resp.get("MessageId")}
