# models/webhook.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime

class WebhookNotification(BaseModel):
    """Webhook notification model from Qualia Marketplace."""
    order_id: str = Field(..., example="QO-123456", description="Qualia order ID")
    notification_type: Literal["order.created"] = Field(..., description="Type of notification")
    timestamp: str = Field(..., example="2025-10-28T10:30:00Z", description="ISO 8601 timestamp")

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Validate order_id starts with QO- prefix."""
        if not v.startswith("QO-"):
            raise ValueError("order_id must start with 'QO-'")
        if len(v) < 4:
            raise ValueError("order_id must have content after 'QO-' prefix")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp is in valid ISO 8601 format."""
        try:
            # Try parsing to ensure it's a valid datetime
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"timestamp must be valid ISO 8601 format: {e}")
        return v