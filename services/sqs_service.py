# services/sqs_service.py
import boto3
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)
sqs = boto3.client('sqs', region_name=settings.AWS_REGION)

def send_to_download_queue(order_id: str, notified_at: str):
    """Send order to download queue for processing."""
    message = {
        "order_id": order_id,
        "notified_at": notified_at
    }
    try:
        response = sqs.send_message(
            QueueUrl=settings.DOWNLOAD_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        logger.info(f"Queued order {order_id} for download", extra={
            "order_id": order_id,
            "message_id": response.get("MessageId")
        })
        return response
    except Exception as e:
        logger.error(f"Failed to queue order {order_id} for download: {str(e)}", extra={
            "order_id": order_id,
            "error": str(e)
        })
        raise

def send_to_processing_queue(order_id: str, s3_key: str, checksum: str = None):
    """Send downloaded order to processing queue."""
    message = {
        "order_id": order_id,
        "s3_key": s3_key
    }
    if checksum:
        message["checksum"] = checksum

    try:
        response = sqs.send_message(
            QueueUrl=settings.PROCESSING_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        logger.info(f"Queued order {order_id} for processing", extra={
            "order_id": order_id,
            "s3_key": s3_key,
            "message_id": response.get("MessageId")
        })
        return response
    except Exception as e:
        logger.error(f"Failed to queue order {order_id} for processing: {str(e)}", extra={
            "order_id": order_id,
            "s3_key": s3_key,
            "error": str(e)
        })
        raise