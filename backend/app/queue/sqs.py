import json
import os
from typing import Any, Dict, List, Optional
import boto3
from app.config import settings


def _get_sqs_client():
    return boto3.client("sqs", region_name=settings.AWS_REGION)


def enqueue_task(payload: Dict[str, Any], group_id: str, deduplication_id: Optional[str] = None) -> Dict[str, Any]:
    """Enqueue a task payload to SQS FIFO queue."""
    if not settings.SQS_URL:
        return {"status": "skipped", "reason": "SQS_URL not configured"}

    sqs = _get_sqs_client()
    kwargs = {
        "QueueUrl": settings.SQS_URL,
        "MessageBody": json.dumps(payload, default=str),
        "MessageGroupId": group_id,
    }
    if deduplication_id:
        kwargs["MessageDeduplicationId"] = deduplication_id

    resp = sqs.send_message(**kwargs)
    return {"status": "enqueued", "message_id": resp.get("MessageId")}


def receive_tasks(max_messages: int = 1, wait_time_seconds: int = 5) -> List[Dict[str, Any]]:
    """Poll messages from SQS FIFO queue."""
    if not settings.SQS_URL:
        return []

    sqs = _get_sqs_client()
    resp = sqs.receive_message(
        QueueUrl=settings.SQS_URL,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_time_seconds,
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
    )
    messages = resp.get("Messages", [])
    results = []
    for msg in messages:
        try:
            body = json.loads(msg["Body"])
        except Exception:
            body = msg["Body"]
        results.append({
            "receipt_handle": msg["ReceiptHandle"],
            "message_id": msg["MessageId"],
            "body": body,
        })
    return results


def delete_task(receipt_handle: str) -> None:
    """Delete a processed message from SQS queue."""
    if not settings.SQS_URL:
        return
    sqs = _get_sqs_client()
    sqs.delete_message(QueueUrl=settings.SQS_URL, ReceiptHandle=receipt_handle)
