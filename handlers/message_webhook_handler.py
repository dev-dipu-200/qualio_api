# handlers/message_webhook_handler.py
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from models.message_webhook import QualiaActivityNotification
from services.dynamodb_service import store_activity
from services.qualia_client import QualiaClient
from utils.auth import verify_webhook_auth

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def receive_activity_webhook(
    notification: QualiaActivityNotification,
    auth = Depends(verify_webhook_auth)
):
    """Receive activity webhook notification from Qualia Marketplace.

    This endpoint handles all Qualia Marketplace activity notifications:
    - order_request: New order received
    - order_cancelled: Order was cancelled
    - order_completed: Order was completed
    - order_revision_requested: Revision requested on order
    - message: New message received
    - documents: New documents added to order

    For 'message' type activities, this will fetch the full message details
    from the Qualia API and store them in DynamoDB.
    """
    request_id = str(uuid.uuid4())[:8]
    start = datetime.now(timezone.utc)

    logger.info(f"Received {notification.type} activity for order {notification.order_id}", extra={
        "order_id": notification.order_id,
        "activity_type": notification.type,
        "request_id": request_id,
        "description": notification.description,
        "message_id": notification.message_id
    })

    try:
        # Store the activity notification
        activity_data = {
            "order_id": notification.order_id,
            "activity_type": notification.type,
            "description": notification.description,
            "message_id": notification.message_id
        }

        store_activity(activity_data)

        # If it's a message notification, fetch and store the full message details
        if notification.type == "message" and notification.message_id:
            try:
                client = QualiaClient()
                # Fetch messages for this order to get the full message details
                messages_response = client.get_messages_list()

                # Find the specific message
                if messages_response and "messages" in messages_response:
                    message = next(
                        (m for m in messages_response["messages"]
                         if m.get("message_id") == notification.message_id),
                        None
                    )

                    if message:
                        # Store the full message details
                        from services.dynamodb_service import store_message
                        message_data = {
                            "order_id": notification.order_id,
                            "message_id": notification.message_id,
                            "message_type": "message",
                            "from_name": message.get("from_name", "Unknown"),
                            "text": message.get("text", ""),
                            "created_date": message.get("created_date", datetime.now(timezone.utc).isoformat()),
                            "read": message.get("read", False),
                            "order_number": message.get("order_number"),
                            "attachments": message.get("attachments", [])
                        }
                        store_message(message_data)
                        logger.info(f"Fetched and stored full message details for message {notification.message_id}")
                    else:
                        logger.warning(f"Message {notification.message_id} not found in messages list")
            except Exception as msg_error:
                # Log but don't fail the webhook if message fetching fails
                logger.error(f"Failed to fetch message details: {str(msg_error)}", extra={
                    "order_id": notification.order_id,
                    "message_id": notification.message_id,
                    "error": str(msg_error)
                })

        # Calculate response time
        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        logger.info(f"Successfully processed {notification.type} activity for order {notification.order_id}", extra={
            "order_id": notification.order_id,
            "activity_type": notification.type,
            "request_id": request_id,
            "response_time_ms": round(duration, 2)
        })

        return {
            "status": "success",
            "message": f"Activity {notification.type} received and processed",
            "order_id": notification.order_id,
            "activity_type": notification.type,
            "request_id": request_id,
            "response_time_ms": round(duration, 2)
        }

    except Exception as e:
        logger.error(f"Failed to process {notification.type} activity for order {notification.order_id}: {str(e)}", extra={
            "order_id": notification.order_id,
            "activity_type": notification.type,
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process activity webhook: {str(e)}"
        )

@router.get("/{order_id}")
async def get_order_messages(
    order_id: str,
    message_type: str = None,
    # auth = Depends(verify_webhook_auth)
):
    """Retrieve all messages for a specific order.

    Args:
        order_id: The order ID to retrieve messages for
        message_type: Optional filter for message type (message.received or message.sent)

    Returns:
        List of messages for the order
    """
    from services.dynamodb_service import get_messages_by_order

    logger.info(f"Retrieving messages for order {order_id}", extra={
        "order_id": order_id,
        "message_type": message_type
    })

    try:
        messages = get_messages_by_order(order_id, message_type)

        return {
            "order_id": order_id,
            "message_type": message_type,
            "count": len(messages),
            "messages": messages
        }

    except Exception as e:
        logger.error(f"Failed to retrieve messages for order {order_id}: {str(e)}", extra={
            "order_id": order_id,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve messages: {str(e)}"
        )
