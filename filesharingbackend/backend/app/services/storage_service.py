"""
S3 / MinIO storage service — handles all object-storage operations.
Uses boto3 for both AWS S3 and MinIO (S3-compatible).
"""
import io
from typing import Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_s3_client():
    """Create and return a boto3 S3 client configured for S3 or MinIO."""
    extra_kwargs = {}
    if settings.STORAGE_BACKEND == "minio":
        extra_kwargs["endpoint_url"] = settings.MINIO_ENDPOINT

    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=BotoConfig(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "adaptive"},
        ),
        **extra_kwargs,
    )


# Singleton client
_client = None


def get_s3_client():
    global _client
    if _client is None:
        _client = _get_s3_client()
    return _client


# ── Bucket Management ─────────────────────────────────────────────────────────
def ensure_bucket_exists(bucket: str = None):
    """Create the bucket if it does not already exist."""
    bucket = bucket or settings.S3_BUCKET_NAME
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=bucket)
        logger.info(f"Bucket '{bucket}' already exists ✓")
    except ClientError:
        try:
            if settings.STORAGE_BACKEND == "minio":
                client.create_bucket(Bucket=bucket)
            else:
                client.create_bucket(
                    Bucket=bucket,
                    CreateBucketConfiguration={
                        "LocationConstraint": settings.AWS_REGION
                    },
                )
            logger.info(f"Bucket '{bucket}' created ✓")
        except ClientError as e:
            logger.error(f"Failed to create bucket '{bucket}': {e}")
            raise


# ── Upload Operations ─────────────────────────────────────────────────────────
def upload_chunk_to_storage(
    user_id: int,
    upload_id: str,
    chunk_index: int,
    data: bytes,
) -> str:
    """
    Upload a single chunk to storage.
    Stored at: uploads/{user_id}/{upload_id}/chunks/{chunk_index}
    Returns the S3 key.
    """
    key = f"uploads/{user_id}/{upload_id}/chunks/{chunk_index}"
    client = get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=data,
    )
    logger.debug(f"Chunk {chunk_index} uploaded → {key}")
    return key


def assemble_chunks_to_final(
    user_id: int,
    upload_id: str,
    total_chunks: int,
    final_filename: str,
) -> str:
    """
    Concatenate all chunk objects into a single final file.
    Uses S3 Multipart Upload API to avoid loading chunks into server RAM.
    Final location: uploads/{user_id}/{upload_id}/{final_filename}
    Returns the final S3 key.
    """
    client = get_s3_client()
    final_key = f"uploads/{user_id}/{upload_id}/{final_filename}"
    bucket = settings.S3_BUCKET_NAME

    # Initialize multipart upload
    mpu = client.create_multipart_upload(Bucket=bucket, Key=final_key)
    part_info = {"Parts": []}

    try:
        # Copy each chunk as a part into the multipart upload
        for i in range(total_chunks):
            chunk_key = f"uploads/{user_id}/{upload_id}/chunks/{i}"
            copy_source = {'Bucket': bucket, 'Key': chunk_key}
            
            response = client.upload_part_copy(
                Bucket=bucket,
                Key=final_key,
                PartNumber=i + 1,
                CopySource=copy_source,
                UploadId=mpu["UploadId"]
            )
            
            part_info["Parts"].append({
                "PartNumber": i + 1,
                "ETag": response["CopyPartResult"]["ETag"]
            })

        # Finalize the multipart upload
        client.complete_multipart_upload(
            Bucket=bucket,
            Key=final_key,
            UploadId=mpu["UploadId"],
            MultipartUpload=part_info
        )
        logger.info(f"Final file assembled via Multipart Upload → {final_key}")
        
    except ClientError as e:
        logger.error(f"Failed to assemble chunks for {final_key}: {e}")
        client.abort_multipart_upload(
            Bucket=bucket,
            Key=final_key,
            UploadId=mpu["UploadId"]
        )
        raise

    # Cleanup chunk objects
    for i in range(total_chunks):
        chunk_key = f"uploads/{user_id}/{upload_id}/chunks/{i}"
        try:
            client.delete_object(Bucket=bucket, Key=chunk_key)
        except ClientError:
            logger.warning(f"Failed to delete chunk {chunk_key}")

    return final_key


# ── Download Operations ───────────────────────────────────────────────────────
def generate_presigned_url(
    key: str,
    expires_in: int = 3600,
    bucket: str = None,
) -> str:
    """Generate a presigned download URL for a stored file."""
    bucket = bucket or settings.S3_BUCKET_NAME

    # For MinIO, we must strictly sign with the exact external-facing endpoint,
    # otherwise S3v4 Signatures will fail due to a Host header mismatch.
    if settings.STORAGE_BACKEND == "minio" and settings.CDN_BASE_URL:
        external_endpoint = settings.CDN_BASE_URL.rsplit("/", 1)[0]
        client_for_presigning = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=BotoConfig(signature_version="s3v4"),
            endpoint_url=external_endpoint,
        )
        return client_for_presigning.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    # Generic S3 Fallback
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def get_file_stream(key: str, bucket: str = None):
    """
    Get a streaming response body for a file in storage.
    Returns (stream, content_length, content_type).
    """
    bucket = bucket or settings.S3_BUCKET_NAME
    client = get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return (
        response["Body"],
        response["ContentLength"],
        response.get("ContentType", "application/octet-stream"),
    )


def get_file_stream_range(
    key: str,
    start_byte: int,
    end_byte: Optional[int] = None,
    bucket: str = None,
):
    """
    Get a partial (range) streaming response for resume-download support.
    Returns (stream, content_length, content_range, total_size).
    """
    bucket = bucket or settings.S3_BUCKET_NAME
    client = get_s3_client()

    # Get total size first
    head = client.head_object(Bucket=bucket, Key=key)
    total_size = head["ContentLength"]

    if end_byte is None or end_byte >= total_size:
        end_byte = total_size - 1

    range_header = f"bytes={start_byte}-{end_byte}"
    response = client.get_object(
        Bucket=bucket, Key=key, Range=range_header
    )
    content_length = end_byte - start_byte + 1
    content_range = f"bytes {start_byte}-{end_byte}/{total_size}"

    return response["Body"], content_length, content_range, total_size


# ── Delete Operations ─────────────────────────────────────────────────────────
def delete_file_from_storage(key: str, bucket: str = None) -> bool:
    """Delete a file from storage. Returns True on success."""
    bucket = bucket or settings.S3_BUCKET_NAME
    client = get_s3_client()
    try:
        client.delete_object(Bucket=bucket, Key=key)
        logger.info(f"Deleted from storage: {key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to delete {key}: {e}")
        return False


def delete_upload_session_files(user_id: int, upload_id: str):
    """Delete all chunk and session files for a given upload session."""
    prefix = f"uploads/{user_id}/{upload_id}/"
    client = get_s3_client()
    try:
        response = client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME, Prefix=prefix
        )
        if "Contents" in response:
            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
            client.delete_objects(
                Bucket=settings.S3_BUCKET_NAME,
                Delete={"Objects": objects},
            )
            logger.info(f"Cleaned up {len(objects)} objects from {prefix}")
    except ClientError as e:
        logger.error(f"Failed to cleanup upload session {prefix}: {e}")
