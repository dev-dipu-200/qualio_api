# tests/conftest.py
import pytest
import os
from unittest.mock import Mock, MagicMock
import boto3
from moto import mock_dynamodb, mock_s3, mock_sqs


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["STAGE"] = "test"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["WEBHOOK_USERNAME"] = "test_user"
    os.environ["WEBHOOK_PASSWORD"] = "test_pass"
    os.environ["QUALIA_API_TOKEN"] = "test_token_123"
    os.environ["INTERNAL_API_TOKEN"] = "internal_token_123"
    os.environ["INTERNAL_API_URL"] = "https://internal-api.example.com/orders"
    os.environ["S3_BUCKET"] = "qualia-orders-test"
    os.environ["DYNAMODB_TABLE"] = "qualia-orders-test"
    os.environ["DOWNLOAD_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789/download-queue-test"
    os.environ["PROCESSING_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789/processing-queue-test"


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='qualia-orders-test',
            KeySchema=[{'AttributeName': 'orderId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'orderId', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table


@pytest.fixture
def mock_s3_bucket():
    """Mock S3 bucket for testing."""
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='qualia-orders-test')
        yield s3


@pytest.fixture
def mock_sqs_queues():
    """Mock SQS queues for testing."""
    with mock_sqs():
        sqs = boto3.client('sqs', region_name='us-east-1')
        download_queue = sqs.create_queue(QueueName='download-queue-test')
        processing_queue = sqs.create_queue(QueueName='processing-queue-test')
        yield {
            'download': download_queue['QueueUrl'],
            'processing': processing_queue['QueueUrl']
        }


@pytest.fixture
def sample_webhook_payload():
    """Sample webhook notification payload."""
    return {
        "order_id": "QO-123456",
        "notification_type": "order.created",
        "timestamp": "2025-10-28T10:30:00Z"
    }


@pytest.fixture
def sample_qualia_order():
    """Sample Qualia order data."""
    return {
        "order_number": "QO-123456",
        "vertical": "title",
        "product_type": "owner_policy",
        "customer_name": "ABC Title Company",
        "due_date": "2025-11-15",
        "properties": [
            {
                "address_1": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zipcode": "94102"
            }
        ]
    }


@pytest.fixture
def sample_sqs_event():
    """Sample SQS Lambda event."""
    return {
        "Records": [
            {
                "messageId": "msg-123",
                "body": '{"order_id": "QO-123456", "notified_at": "2025-10-28T10:30:00Z"}'
            }
        ]
    }


@pytest.fixture
def sample_processing_event():
    """Sample processing SQS event."""
    return {
        "Records": [
            {
                "messageId": "msg-456",
                "body": '{"order_id": "QO-123456", "s3_key": "orders/2025/10/QO-123456/raw.json", "checksum": "abc123"}'
            }
        ]
    }
