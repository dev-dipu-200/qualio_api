# test_message_webhook.py
"""
Test script for message webhook endpoint.

This script demonstrates how to send test requests to the message webhook endpoint.
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_ENDPOINT = f"{BASE_URL}/webhook/messages"
GET_MESSAGES_ENDPOINT = f"{BASE_URL}/webhook/messages"

# Webhook credentials (should match your .env settings)
AUTH = ("webhook_user", "webhook_pass")  # Update with your actual credentials

def test_message_received_webhook():
    """Test webhook for received message."""
    payload = {
        "order_id": "QO-123456",
        "message_id": "MSG-001",
        "order_number": "ORD-2025-001",
        "from_name": "John Smith",
        "text": "Hello, I have a question about this order.",
        "created_date": datetime.utcnow().isoformat() + "Z",
        "read": False,
        "attachments": [
            {
                "_id": "ATT-001",
                "name": "document.pdf",
                "url": "https://example.com/files/document.pdf",
                "tag": "contract"
            }
        ],
        "message_type": "message.received",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(f"\n{'='*60}")
    print("Testing MESSAGE RECEIVED webhook...")
    print(f"{'='*60}")
    print(f"\nPayload:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=payload,
            auth=AUTH,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Message received webhook processed successfully!")
        else:
            print(f"\n✗ Error: {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

def test_message_sent_webhook():
    """Test webhook for sent message."""
    payload = {
        "order_id": "QO-123456",
        "message_id": "MSG-002",
        "order_number": "ORD-2025-001",
        "from_name": "Support Team",
        "text": "Thank you for your message. We will review your order and get back to you shortly.",
        "created_date": datetime.utcnow().isoformat() + "Z",
        "read": False,
        "attachments": [],
        "message_type": "message.sent",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    print(f"\n{'='*60}")
    print("Testing MESSAGE SENT webhook...")
    print(f"{'='*60}")
    print(f"\nPayload:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_ENDPOINT,
            json=payload,
            auth=AUTH,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Message sent webhook processed successfully!")
        else:
            print(f"\n✗ Error: {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

def test_get_messages(order_id="QO-123456", message_type=None):
    """Test retrieving messages for an order."""
    endpoint = f"{GET_MESSAGES_ENDPOINT}/{order_id}"
    params = {}
    if message_type:
        params["message_type"] = message_type

    print(f"\n{'='*60}")
    print(f"Testing GET messages for order: {order_id}")
    if message_type:
        print(f"Filter: {message_type}")
    print(f"{'='*60}")

    try:
        response = requests.get(
            endpoint,
            params=params,
            auth=AUTH,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Messages retrieved successfully!")
        else:
            print(f"\n✗ Error: {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MESSAGE WEBHOOK TEST SUITE")
    print("="*60)
    print("\nMake sure your FastAPI server is running at:", BASE_URL)
    print("Update AUTH credentials in this script to match your .env settings")

    # Test 1: Received message webhook
    test_message_received_webhook()

    # Test 2: Sent message webhook
    test_message_sent_webhook()

    # Test 3: Get all messages for an order
    test_get_messages("QO-123456")

    # Test 4: Get only received messages
    test_get_messages("QO-123456", "message.received")

    # Test 5: Get only sent messages
    test_get_messages("QO-123456", "message.sent")

    print(f"\n{'='*60}")
    print("TEST SUITE COMPLETED")
    print("="*60)
