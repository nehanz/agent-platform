import os
from typing import List, Optional
import boto3
from app.config import settings


def _get_s3_client():
    return boto3.client("s3", region_name=settings.AWS_REGION)


def upload_document(key: str, body: bytes, content_type: Optional[str] = None) -> None:
    """Upload a document to the configured S3 bucket."""
    s3 = _get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=body,
        **extra_args
    )


def download_document(key: str) -> bytes:
    """Download a document bytes from the configured S3 bucket."""
    s3 = _get_s3_client()
    resp = s3.get_object(Bucket=settings.S3_BUCKET, Key=key)
    return resp["Body"].read()


def list_documents(prefix: str = "") -> List[str]:
    """List document keys in the configured S3 bucket matching prefix."""
    s3 = _get_s3_client()
    resp = s3.list_objects_v2(Bucket=settings.S3_BUCKET, Prefix=prefix)
    return [item["Key"] for item in resp.get("Contents", [])]


def delete_document(key: str) -> None:
    """Delete a document from S3."""
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)
