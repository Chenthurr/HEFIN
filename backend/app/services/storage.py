"""
S3-compatible object storage (Section 16: Object Storage).
Works against MinIO locally and S3-compatible production storage.
"""

import uuid

import boto3
from botocore.client import Config

from app.core.config import get_settings

settings = get_settings()

_client = boto3.client(
    "s3",
    endpoint_url=settings.minio_endpoint,
    aws_access_key_id=settings.minio_access_key,
    aws_secret_access_key=settings.minio_secret_key,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

BUCKET = "hefin-documents"


def ensure_bucket() -> None:
    existing = {b["Name"] for b in _client.list_buckets().get("Buckets", [])}
    if BUCKET not in existing:
        _client.create_bucket(Bucket=BUCKET)


def upload_bytes(data: bytes, content_type: str, original_filename: str) -> str:
    ensure_bucket()
    key = f"{uuid.uuid4()}-{original_filename}"
    _client.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)
    return key


def download_bytes(storage_key: str) -> bytes:
    obj = _client.get_object(Bucket=BUCKET, Key=storage_key)
    return obj["Body"].read()
