# services/dynamodb_service.py
import boto3
import logging
import os
from botocore.exceptions import ClientError
from config.settings import settings
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Check if using LocalStack for local development
USE_LOCALSTACK = os.getenv('USE_LOCALSTACK', 'false').lower() == 'true'
LOCALSTACK_ENDPOINT = os.getenv('LOCALSTACK_ENDPOINT', 'http://localhost:4566')

if USE_LOCALSTACK:
    logger.info(f"Using LocalStack DynamoDB at {LOCALSTACK_ENDPOINT}")
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=settings.AWS_REGION,
        endpoint_url=LOCALSTACK_ENDPOINT
    )
else:
    logger.info(f"Using AWS DynamoDB in region {settings.AWS_REGION}")
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)

table = dynamodb.Table(settings.DYNAMODB_TABLE)

def put_metadata(order_id: str, status: str, extra: dict = None):
    """Store or update order metadata in DynamoDB."""
    item = {
        'orderId': order_id,
        'timestamp': int(datetime.utcnow().timestamp() * 1000),
        'status': status,
        'notified_at': datetime.utcnow().isoformat() + "Z",
        **(extra or {})
    }
    try:
        table.put_item(Item=item)
        logger.info(f"Updated order {order_id} status to {status}", extra={
            "order_id": order_id,
            "status": status,
            "metadata": extra
        })
    except ClientError as e:
        logger.error(f"DynamoDB write failed for order {order_id}: {str(e)}", extra={
            "order_id": order_id,
            "status": status,
            "error": str(e),
            "error_code": e.response.get('Error', {}).get('Code')
        })
        raise RuntimeError(f"DynamoDB write failed: {e}")

def store_activity(activity_data: dict):
    """Store Qualia activity notification in DynamoDB.

    Args:
        activity_data: Dictionary containing activity information including:
            - order_id: Order ID
            - activity_type: Type of activity (order_request, message, etc.)
            - description: Human-readable description
            - message_id: Message ID (optional, only for message type)
    """
    # Create composite key for activities
    pk = f"ACTIVITY#{activity_data['order_id']}"
    timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
    sk = f"{activity_data['activity_type']}#{timestamp_ms}"

    item = {
        'PK': pk,
        'SK': sk,
        'orderId': activity_data['order_id'],
        'activityType': activity_data['activity_type'],
        'description': activity_data['description'],
        'timestamp': timestamp_ms,
        'receivedAt': datetime.utcnow().isoformat() + "Z"
    }

    # Add message_id if present
    if activity_data.get('message_id'):
        item['messageId'] = activity_data['message_id']

    try:
        table.put_item(Item=item)
        logger.info(f"Stored {activity_data['activity_type']} activity for order {activity_data['order_id']}", extra={
            "order_id": activity_data['order_id'],
            "activity_type": activity_data['activity_type'],
            "message_id": activity_data.get('message_id')
        })
    except ClientError as e:
        logger.error(f"DynamoDB write failed for activity: {str(e)}", extra={
            "order_id": activity_data['order_id'],
            "activity_type": activity_data['activity_type'],
            "error": str(e),
            "error_code": e.response.get('Error', {}).get('Code')
        })
        raise RuntimeError(f"DynamoDB write failed: {e}")

def store_message(message_data: dict):
    """Store Qualia message in DynamoDB.

    Args:
        message_data: Dictionary containing message information including:
            - order_id: Order ID
            - message_id: Unique message ID
            - message_type: Type of message (message.received or message.sent)
            - from_name: Sender name
            - text: Message content
            - created_date: Message creation timestamp
            - read: Read status
            - attachments: List of attachments (optional)
            - order_number: Order number (optional)
    """
    # Create composite key: order_id + message_id
    pk = f"MESSAGE#{message_data['order_id']}"
    sk = f"{message_data['message_type']}#{message_data['message_id']}"

    item = {
        'PK': pk,
        'SK': sk,
        'orderId': message_data['order_id'],
        'messageId': message_data['message_id'],
        'messageType': message_data['message_type'],
        'fromName': message_data['from_name'],
        'text': message_data['text'],
        'createdDate': message_data['created_date'],
        'read': message_data.get('read', False),
        'timestamp': int(datetime.utcnow().timestamp() * 1000),
        'storedAt': datetime.utcnow().isoformat() + "Z"
    }

    # Add optional fields
    if message_data.get('order_number'):
        item['orderNumber'] = message_data['order_number']

    if message_data.get('attachments'):
        item['attachments'] = message_data['attachments']

    try:
        table.put_item(Item=item)
        logger.info(f"Stored message {message_data['message_id']} for order {message_data['order_id']}", extra={
            "order_id": message_data['order_id'],
            "message_id": message_data['message_id'],
            "message_type": message_data['message_type']
        })
    except ClientError as e:
        logger.error(f"DynamoDB write failed for message {message_data['message_id']}: {str(e)}", extra={
            "order_id": message_data['order_id'],
            "message_id": message_data['message_id'],
            "error": str(e),
            "error_code": e.response.get('Error', {}).get('Code')
        })
        raise RuntimeError(f"DynamoDB write failed: {e}")

def get_messages_by_order(order_id: str, message_type: str = None):
    """Retrieve messages for a specific order from DynamoDB.

    Args:
        order_id: The order ID to retrieve messages for
        message_type: Optional message type filter (message.received or message.sent)

    Returns:
        List of message items
    """
    pk = f"MESSAGE#{order_id}"

    try:
        if message_type:
            # Query with message type filter
            response = table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': pk,
                    ':sk_prefix': message_type
                }
            )
        else:
            # Query all messages for the order
            response = table.query(
                KeyConditionExpression='PK = :pk',
                ExpressionAttributeValues={
                    ':pk': pk
                }
            )

        messages = response.get('Items', [])
        logger.info(f"Retrieved {len(messages)} messages for order {order_id}", extra={
            "order_id": order_id,
            "message_type": message_type,
            "count": len(messages)
        })
        return messages

    except ClientError as e:
        logger.error(f"DynamoDB query failed for order {order_id}: {str(e)}", extra={
            "order_id": order_id,
            "error": str(e),
            "error_code": e.response.get('Error', {}).get('Code')
        })
        raise RuntimeError(f"DynamoDB query failed: {e}")