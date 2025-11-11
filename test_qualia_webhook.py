#!/usr/bin/env python3
# test_qualia_webhook.py
"""
Test script for Qualia Marketplace Activity Webhook.

This script tests all activity types that Qualia sends via webhook:
- order_request
- order_cancelled
- order_completed
- order_revision_requested
- message
- documents
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
WEBHOOK_ENDPOINT = f"{BASE_URL}/webhook/activity"

# Webhook credentials (should match your .env settings)
AUTH = ("webhook_user", "webhook_pass")  # Update with your actual credentials

def test_activity(activity_type, payload, description):
    """Test a specific activity type."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"Activity Type: {activity_type}")
    print(f"{'='*70}")
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
            print(f"\n✓ {activity_type} webhook processed successfully!")
            return True
        else:
            print(f"\n✗ Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

def test_order_request():
    """Test order_request activity (new order received)."""
    payload = {
        "description": "You've received an order for a Title Search Plus in San Francisco County, California.",
        "type": "order_request",
        "order_id": "bK8bg5tajNkDpDk25"
    }
    return test_activity("order_request", payload, "New Order Request")

def test_order_cancelled():
    """Test order_cancelled activity."""
    payload = {
        "description": "Boston Legal has cancelled order #TEST-2018-1.",
        "type": "order_cancelled",
        "order_id": "bK8bg5tajNkDpDk25"
    }
    return test_activity("order_cancelled", payload, "Order Cancelled")

def test_order_completed():
    """Test order_completed activity."""
    payload = {
        "description": "Boston Legal has accepted order #TEST-2018-1.",
        "type": "order_completed",
        "order_id": "bK8bg5tajNkDpDk25"
    }
    return test_activity("order_completed", payload, "Order Completed")

def test_order_revision_requested():
    """Test order_revision_requested activity."""
    payload = {
        "description": "Boston Legal has requested a change on order #TEST-2018-1.",
        "type": "order_revision_requested",
        "order_id": "bK8bg5tajNkDpDk25"
    }
    return test_activity("order_revision_requested", payload, "Order Revision Requested")

def test_message():
    """Test message activity."""
    payload = {
        "description": "Marty McFly sent you a message.",
        "type": "message",
        "order_id": "bK8bg5tajNkDpDk25",
        "message_id": "LEPAjMB43myH8aGcP"
    }
    return test_activity("message", payload, "Message Received")

def test_documents():
    """Test documents activity."""
    payload = {
        "description": "Boston Legal has sent you additional documents on order #TEST-2018-1",
        "type": "documents",
        "order_id": "bK8bg5tajNkDpDk25"
    }
    return test_activity("documents", payload, "Documents Added")

def test_validation_errors():
    """Test validation error handling."""
    print(f"\n{'='*70}")
    print("Testing: Validation Error Handling")
    print(f"{'='*70}")

    # Test with missing required fields
    invalid_payloads = [
        {
            "name": "Missing order_id",
            "payload": {
                "description": "Test",
                "type": "message"
            }
        },
        {
            "name": "Missing type",
            "payload": {
                "description": "Test",
                "order_id": "test-123"
            }
        },
        {
            "name": "Invalid type",
            "payload": {
                "description": "Test",
                "type": "invalid_type",
                "order_id": "test-123"
            }
        },
        {
            "name": "Empty order_id",
            "payload": {
                "description": "Test",
                "type": "message",
                "order_id": ""
            }
        }
    ]

    results = []
    for test_case in invalid_payloads:
        print(f"\n  Test: {test_case['name']}")
        try:
            response = requests.post(
                WEBHOOK_ENDPOINT,
                json=test_case['payload'],
                auth=AUTH,
                timeout=10
            )
            if response.status_code in [400, 422]:
                print(f"  ✓ Correctly rejected with status {response.status_code}")
                results.append(True)
            else:
                print(f"  ✗ Unexpected status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append(False)

    return all(results)

def main():
    print("\n" + "="*70)
    print("QUALIA MARKETPLACE ACTIVITY WEBHOOK TEST SUITE")
    print("="*70)
    print(f"\nEndpoint: {WEBHOOK_ENDPOINT}")
    print("Make sure your FastAPI server is running!")
    print("Update AUTH credentials to match your .env settings")

    results = []

    # Test all activity types
    print("\n" + "="*70)
    print("PART 1: Testing All Activity Types")
    print("="*70)

    results.append(("Order Request", test_order_request()))
    results.append(("Order Cancelled", test_order_cancelled()))
    results.append(("Order Completed", test_order_completed()))
    results.append(("Order Revision Requested", test_order_revision_requested()))
    results.append(("Message", test_message()))
    results.append(("Documents", test_documents()))

    # Test validation
    print("\n" + "="*70)
    print("PART 2: Testing Validation")
    print("="*70)
    results.append(("Validation Errors", test_validation_errors()))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:30s} {status}")

    print(f"\n{passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")

    return 0 if passed == total else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
