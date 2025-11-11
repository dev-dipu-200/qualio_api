#!/usr/bin/env python3
"""
Verification script to ensure all components are properly set up.
"""

def verify_imports():
    """Verify all required imports work."""
    print("Verifying imports...")
    try:
        from models.message_webhook import QualiaActivityNotification
        print("✓ Activity webhook models imported successfully")

        from handlers.message_webhook_handler import router
        print("✓ Message webhook handler imported successfully")

        from services.dynamodb_service import store_message, get_messages_by_order
        print("✓ DynamoDB service functions imported successfully")

        from main import app
        print("✓ Main FastAPI app imported successfully")

        return True
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        return False

def verify_pydantic_model():
    """Verify Pydantic model works with Qualia activity format."""
    print("\nVerifying Pydantic model with Qualia activity format...")
    try:
        from models.message_webhook import QualiaActivityNotification

        # Test message activity
        test_data = {
            "description": "Marty McFly sent you a message.",
            "type": "message",
            "order_id": "bK8bg5tajNkDpDk25",
            "message_id": "LEPAjMB43myH8aGcP"
        }

        notification = QualiaActivityNotification(**test_data)
        print(f"✓ Model created successfully")
        print(f"  - Type: {notification.type}")
        print(f"  - Order ID: {notification.order_id}")
        print(f"  - Message ID: {notification.message_id}")

        # Test order activity without message_id
        test_data2 = {
            "description": "You've received an order for a Title Search Plus.",
            "type": "order_request",
            "order_id": "bK8bg5tajNkDpDk25"
        }

        notification2 = QualiaActivityNotification(**test_data2)
        print(f"✓ Order activity model works (message_id is optional)")

        return True
    except Exception as e:
        print(f"✗ Model verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_routes():
    """Verify routes are registered."""
    print("\nVerifying routes...")
    try:
        from main import app
        routes = [route.path for route in app.routes]

        if "/webhook/activity" in routes or any("/webhook/activity" in r for r in routes):
            print("✓ Activity webhook route registered at /webhook/activity")
        else:
            print("✗ Activity webhook route NOT found")
            print(f"Available routes: {routes}")
            return False

        return True
    except Exception as e:
        print(f"✗ Route verification failed: {str(e)}")
        return False

def main():
    print("="*60)
    print("SETUP VERIFICATION")
    print("="*60)

    results = []

    results.append(("Imports", verify_imports()))
    results.append(("Pydantic Model", verify_pydantic_model()))
    results.append(("Routes", verify_routes()))

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ All verifications passed! Ready to run the application.")
        print("\nTo start the server, run:")
        print("  python main.py")
        print("  OR")
        print("  uvicorn main:app --reload")
    else:
        print("\n✗ Some verifications failed. Please check the errors above.")

    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
