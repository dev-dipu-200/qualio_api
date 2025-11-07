# tests/test_webhook_handler.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app


client = TestClient(app)


class TestWebhookHandler:
    """Tests for webhook handler endpoint."""

    def test_receive_webhook_success(self):
        """Test successful webhook reception."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        with patch('handlers.webhook_handler.put_metadata') as mock_db, \
             patch('handlers.webhook_handler.send_to_download_queue') as mock_sqs:

            response = client.post(
                "/webhook",
                json=payload,
                auth=("test_user", "test_pass")
            )

            assert response.status_code == 200
            data = response.json()
            assert data["order_id"] == "QO-123456"
            assert "request_id" in data
            assert "response_time_ms" in data
            assert data["message"] == "Order received and queued for processing"

            # Verify DynamoDB was called
            mock_db.assert_called_once()
            call_args = mock_db.call_args
            assert call_args[1]["order_id"] == "QO-123456"
            assert call_args[1]["status"] == "NOTIFIED"

            # Verify SQS was called
            mock_sqs.assert_called_once_with(
                order_id="QO-123456",
                notified_at="2025-10-28T10:30:00Z"
            )

    def test_webhook_invalid_auth(self):
        """Test webhook with invalid authentication."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        response = client.post(
            "/webhook",
            json=payload,
            auth=("wrong_user", "wrong_pass")
        )

        assert response.status_code == 401

    def test_webhook_missing_auth(self):
        """Test webhook without authentication."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        response = client.post("/webhook", json=payload)
        assert response.status_code == 401

    def test_webhook_invalid_order_id(self):
        """Test webhook with invalid order_id format."""
        payload = {
            "order_id": "INVALID-123",  # Doesn't start with QO-
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        response = client.post(
            "/webhook",
            json=payload,
            auth=("test_user", "test_pass")
        )

        assert response.status_code == 422  # Validation error

    def test_webhook_invalid_timestamp(self):
        """Test webhook with invalid timestamp format."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "invalid-timestamp"
        }

        response = client.post(
            "/webhook",
            json=payload,
            auth=("test_user", "test_pass")
        )

        assert response.status_code == 422  # Validation error

    def test_webhook_invalid_notification_type(self):
        """Test webhook with invalid notification type."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.invalid",  # Not in allowed types
            "timestamp": "2025-10-28T10:30:00Z"
        }

        response = client.post(
            "/webhook",
            json=payload,
            auth=("test_user", "test_pass")
        )

        assert response.status_code == 422  # Validation error

    def test_webhook_database_error(self):
        """Test webhook when database fails."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        with patch('handlers.webhook_handler.put_metadata', side_effect=Exception("DB Error")):
            response = client.post(
                "/webhook",
                json=payload,
                auth=("test_user", "test_pass")
            )

            assert response.status_code == 500
            assert "Failed to process webhook" in response.json()["detail"]

    def test_webhook_sqs_error(self):
        """Test webhook when SQS fails."""
        payload = {
            "order_id": "QO-123456",
            "notification_type": "order.created",
            "timestamp": "2025-10-28T10:30:00Z"
        }

        with patch('handlers.webhook_handler.put_metadata'), \
             patch('handlers.webhook_handler.send_to_download_queue', side_effect=Exception("SQS Error")):

            response = client.post(
                "/webhook",
                json=payload,
                auth=("test_user", "test_pass")
            )

            assert response.status_code == 500
            assert "Failed to process webhook" in response.json()["detail"]

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "qualia-webhook-api"
        assert data["version"] == "1.0.0"
