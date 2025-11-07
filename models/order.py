# models/order.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enum."""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    SUBMITTED = "SUBMITTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    COMPLETED = "COMPLETED"
    RESUBMITTED = "RESUBMITTED"
    RESUBMISSION_ACCEPTED = "RESUBMISSION_ACCEPTED"
    PREORDER = "PREORDER"
    OPEN = "OPEN"


class GetOrdersInput(BaseModel):
    """Input for getting a list of orders."""
    status: Optional[OrderStatus] = Field(None, description="Filter orders by status")
    customer_id: Optional[str] = Field(None, description="Filter by customer ID")
    order_number: Optional[str] = Field(None, description="Filter by order number")
    limit: Optional[int] = Field(None, description="Limit number of results")
    offset: Optional[int] = Field(None, description="Offset for pagination")

    class Config:
        use_enum_values = True


class GetOrdersResponse(BaseModel):
    """Response from orders query - flexible model to handle list of orders."""
    orders: Optional[List[Dict[str, Any]]] = Field(None, description="List of orders")

    class Config:
        extra = "allow"  # Allow additional fields from the API


class GetOrderInput(BaseModel):
    """Input for getting an order by ID."""
    order_id: str = Field(..., description="The order ID to retrieve", alias="_id")


class GetOrderResponse(BaseModel):
    """Response from GetOrder query - flexible model to handle complex nested structure."""
    order: Optional[Dict[str, Any]] = Field(None, description="The complete order data")
    outstanding_tasks: Optional[List[str]] = Field(None, description="List of outstanding tasks")

    class Config:
        extra = "allow"  # Allow additional fields from the API


class GetOrderResult(BaseModel):
    """Complete result from GetOrder query."""
    order: GetOrderResponse
