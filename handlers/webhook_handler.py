# handlers/webhook_handler.py
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from models.webhook import WebhookNotification
from services.dynamodb_service import put_metadata
from services.sqs_service import send_to_download_queue
from utils.auth import verify_webhook_auth

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def receive_webhook(
    notification: WebhookNotification,
    auth = Depends(verify_webhook_auth)
):
    """Receive webhook notification from Qualia and queue for processing."""
    request_id = str(uuid.uuid4())[:8]
    start = datetime.utcnow()

    logger.info(f"Received webhook for order {notification.order_id}", extra={
        "order_id": notification.order_id,
        "request_id": request_id,
        "notification_type": notification.notification_type
    })

    try:
        # 1. Write NOTIFIED to DynamoDB
        put_metadata(
            order_id=notification.order_id,
            status="NOTIFIED",
            extra={"request_id": request_id}
        )

        # 2. Send to Download SQS
        send_to_download_queue(
            order_id=notification.order_id,
            notified_at=notification.timestamp
        )

        # 3. Respond fast (<50ms)
        duration = (datetime.utcnow() - start).total_seconds() * 1000

        logger.info(f"Successfully processed webhook for order {notification.order_id}", extra={
            "order_id": notification.order_id,
            "request_id": request_id,
            "response_time_ms": round(duration, 2)
        })

        return {
            "message": "Order received and queued for processing",
            "order_id": notification.order_id,
            "request_id": request_id,
            "response_time_ms": round(duration, 2)
        }

    except Exception as e:
        logger.error(f"Failed to process webhook for order {notification.order_id}: {str(e)}", extra={
            "order_id": notification.order_id,
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )
    
