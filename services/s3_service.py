# services/s3_service.py
import boto3
import json
import hashlib
import logging
from config.settings import settings
from datetime import datetime

logger = logging.getLogger(__name__)
s3 = boto3.client('s3', region_name=settings.AWS_REGION)

def upload_raw_payload(order_id: str, payload: dict):
    """Upload raw order payload to S3 with checksum."""
    now = datetime.utcnow()
    key = f"orders/{now.year}/{now.month:02d}/{order_id}/raw.json"
    body = json.dumps(payload).encode('utf-8')
    checksum = hashlib.sha256(body).hexdigest()

    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=body,
            ContentType='application/json',
            Metadata={'checksum': checksum}
        )
        logger.info(f"Uploaded order {order_id} to S3", extra={
            "order_id": order_id,
            "s3_key": key,
            "checksum": checksum,
            "size_bytes": len(body)
        })
        return key, checksum
    except Exception as e:
        logger.error(f"Failed to upload order {order_id} to S3: {str(e)}", extra={
            "order_id": order_id,
            "s3_key": key,
            "error": str(e)
        })
        raise