# models/cancel_order.py
from pydantic import BaseModel, Field
from typing import Optional


class StatusDetails(BaseModel):
    """Order status details."""
    open: Optional[bool] = None
    pending: Optional[bool] = None
    accepted: Optional[bool] = None
    declined: Optional[bool] = None
    cancelled: Optional[bool] = None
    submitted: Optional[bool] = None
    revision_required: Optional[bool] = None
    completed: Optional[bool] = None
    resubmitted: Optional[bool] = None
    resubmission_accepted: Optional[bool] = None
    preorder: Optional[bool] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None
    revision_required_reason: Optional[str] = None
    created_date: Optional[str] = None
    closed_date: Optional[str] = None


class CancelOrderResponse(BaseModel):
    """Response from cancel order mutation."""
    status: Optional[str] = None
    status_details: Optional[StatusDetails] = None


class CancelOrderInput(BaseModel):
    """Input for canceling an order."""
    order_id: str = Field(..., description="The order ID to cancel")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation")


class CancelOrderResult(BaseModel):
    """Complete result from cancelOrder mutation."""
    cancelOrder: CancelOrderResponse
