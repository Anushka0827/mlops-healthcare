import os
import boto3
from botocore.exceptions import ClientError
from loguru import logger

# Try loading from environment
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

def get_s3_client():
    """Initialize S3 client based on available environment credentials."""
    try:
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            return boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        else:
            # Fallback to local boto3 credentials (if configured e.g., on EC2 iam role or local ~/.aws/credentials)
            return boto3.client('s3')
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return None

def upload_model_to_s3(file_path: str, object_name: str = None) -> bool:
    """Upload a file to an S3 bucket."""
    if not AWS_S3_BUCKET:
        logger.warning("AWS_S3_BUCKET not set. Skipping S3 upload.")
        return False
        
    s3_client = get_s3_client()
    if not s3_client:
        return False

    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        logger.info(f"Uploading {file_path} to s3://{AWS_S3_BUCKET}/{object_name}")
        s3_client.upload_file(file_path, AWS_S3_BUCKET, object_name)
    except ClientError as e:
        logger.error(f"S3 Upload failed: {e}")
        return False
    return True

def download_model_from_s3(object_name: str, file_path: str) -> bool:
    """Download a file from an S3 bucket."""
    if not AWS_S3_BUCKET:
        logger.warning("AWS_S3_BUCKET not set. Will use local files if they exist.")
        return False

    s3_client = get_s3_client()
    if not s3_client:
        return False

    try:
        logger.info(f"Downloading s3://{AWS_S3_BUCKET}/{object_name} to {file_path}")
        s3_client.download_file(AWS_S3_BUCKET, object_name, file_path)
    except ClientError as e:
        logger.error(f"S3 Download failed: {e}")
        return False
    return True
