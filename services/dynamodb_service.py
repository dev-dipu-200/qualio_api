# services/dynamodb_service.py
import boto3
import logging
from botocore.exceptions import ClientError
from config.settings import settings
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)
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