import os
from dotenv import load_dotenv

load_dotenv()

USE_SPACES = bool(os.getenv("SPACES_KEY"))

if USE_SPACES:
    import boto3
    _client = boto3.client(
        's3',
        region_name=os.environ["SPACES_REGION"],
        endpoint_url=os.environ["SPACES_ENDPOINT"],
        aws_access_key_id=os.environ["SPACES_KEY"],
        aws_secret_access_key=os.environ["SPACES_SECRET"]
    )
    _bucket = os.environ["SPACES_BUCKET"]
    _endpoint = os.environ["SPACES_ENDPOINT"]

_local_base = os.path.join(os.path.dirname(__file__), "uploads")


def save_file(file_bytes: bytes, folder: str, filename: str, content_type: str = "application/octet-stream") -> str:
    """Save to DigitalOcean Spaces (production) or local uploads/ (dev)."""
    if USE_SPACES:
        key = f"{folder}/{filename}"
        _client.put_object(
            Bucket=_bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ACL='public-read'
        )
        return f"{_endpoint}/{_bucket}/{key}"
    else:
        dir_path = os.path.join(_local_base, folder)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, filename), "wb") as f:
            f.write(file_bytes)
        return f"uploads/{folder}/{filename}"
