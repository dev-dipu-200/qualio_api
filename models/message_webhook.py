# models/message_webhook.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

class QualiaActivityNotification(BaseModel):
    """Webhook notification model for Qualia Marketplace Activity events.

    This model matches the actual Qualia Marketplace webhook payload format.
    All activity notifications follow this structure.
    """
    description: str = Field(..., description="Human-readable description of the activity")
    type: Literal[
        "order_request",
        "order_cancelled",
        "order_completed",
        "order_revision_requested",
        "message",
        "documents"
    ] = Field(..., description="Type of activity notification")
    order_id: str = Field(..., description="Qualia order ID")
    message_id: Optional[str] = Field(None, description="Message ID (only present for message type)")

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Validate order_id is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("order_id cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "description": "Marty McFly sent you a message.",
                    "type": "message",
                    "order_id": "bK8bg5tajNkDpDk25",
                    "message_id": "LEPAjMB43myH8aGcP"
                },
                {
                    "description": "You've received an order for a Title Search Plus in San Francisco ...",
                    "type": "order_request",
                    "order_id": "bK8bg5tajNkDpDk25"
                }
            ]
        }
