from fastapi import APIRouter, HTTPException, Depends, Query
from services.qualia_client import QualiaClient
from models.cancel_order import CancelOrderInput, CancelOrderResult
from models.order import OrderStatus
from models.order_operations import (
    DeclineOrderInput,
    SubmitOrderInput,
    MessageInput,
    AddFilesInput,
    RemoveFilesInput,
    FulfillTitleSearchInputWrapper
)
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def get_qualia_client() -> QualiaClient:
    """Dependency to get QualiaClient instance."""
    return QualiaClient()


@router.get("/", response_model=Dict[str, Any])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    order_number: Optional[str] = Query(None, description="Filter by order number"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    offset: Optional[int] = Query(None, description="Offset for pagination"),
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Retrieve a list of orders with optional filters via Qualia GraphQL API.

    Args:
        status: Filter orders by status (PENDING, ACCEPTED, DECLINED, etc.)
        customer_id: Filter by customer ID
        order_number: Filter by order number
        limit: Limit number of results
        offset: Offset for pagination
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: List of orders matching the filters

    Raises:
        HTTPException: If the orders retrieval fails
    """
    try:
        # Build filters dict, excluding None values
        filters = {}
        if status:
            filters["status"] = status.value
        if customer_id:
            filters["customer_id"] = customer_id
        if order_number:
            filters["order_number"] = order_number
        if limit:
            filters["limit"] = limit
        if offset:
            filters["offset"] = offset

        logger.info(f"Received get orders request with filters: {filters}")

        result = client.get_orders(filters=filters if filters else None)

        logger.info("Successfully processed get orders request")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to fetch orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{order_id}", response_model=Dict[str, Any])
async def get_order(
    order_id: str,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Retrieve detailed order information by order ID via Qualia GraphQL API.

    Args:
        order_id: The unique identifier of the order to retrieve
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: Complete order data including all nested fields

    Raises:
        HTTPException: If the order retrieval fails
    """
    try:
        logger.info(f"Received get order request for {order_id}")

        result = client.get_order(order_id=order_id)

        logger.info(f"Successfully processed get order request for {order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to fetch order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/accept", response_model=Dict[str, Any])
async def accept_order(
    order_id: str,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Accept an order via Qualia GraphQL API.

    Args:
        order_id: The unique identifier of the order to accept
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: The updated order data after acceptance

    Raises:
        HTTPException: If the acceptance fails
    """
    try:
        logger.info(f"Received accept order request for {order_id}")

        result = client.accept_order(order_id=order_id)

        logger.info(f"Successfully processed accept order request for {order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to accept order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error accepting order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 


@router.post("/cancel", response_model=CancelOrderResult)
async def cancel_order(
    cancel_input: CancelOrderInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Cancel an order via Qualia GraphQL API.

    Args:
        cancel_input: Order cancellation details including order_id and optional cancellation_reason
        client: QualiaClient instance (injected via dependency)

    Returns:
        CancelOrderResult: The result of the cancellation including status and status details

    Raises:
        HTTPException: If the cancellation fails
    """
    try:
        logger.info(f"Received cancel order request for {cancel_input.order_id}")

        result = client.cancel_order(
            order_id=cancel_input.order_id,
            cancellation_reason=cancel_input.cancellation_reason
        )

        logger.info(f"Successfully processed cancel order request for {cancel_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to cancel order {cancel_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error cancelling order {cancel_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/decline", response_model=Dict[str, Any])
async def decline_order(
    decline_input: DeclineOrderInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Decline an order via Qualia GraphQL API.

    Args:
        decline_input: Order decline details including order_id and optional decline_reason
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: The updated order status after declining

    Raises:
        HTTPException: If the decline operation fails
    """
    try:
        logger.info(f"Received decline order request for {decline_input.order_id}")

        result = client.decline_order(
            order_id=decline_input.order_id,
            decline_reason=decline_input.decline_reason
        )

        logger.info(f"Successfully processed decline order request for {decline_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to decline order {decline_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error declining order {decline_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/submit", response_model=Dict[str, Any])
async def submit_order(
    submit_input: SubmitOrderInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Submit an order via Qualia GraphQL API.

    Args:
        submit_input: Order submission details including order_id
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: The updated order status after submission

    Raises:
        HTTPException: If the submission fails
    """
    try:
        logger.info(f"Received submit order request for {submit_input.order_id}")

        result = client.submit_order(order_id=submit_input.order_id)

        logger.info(f"Successfully processed submit order request for {submit_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to submit order {submit_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error submitting order {submit_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/message", response_model=Dict[str, Any])
async def send_message(
    message_input: MessageInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Send a message to an order via Qualia GraphQL API.

    Args:
        message_input: Message details including order_id, text, and optional attachments
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: Success status of the message

    Raises:
        HTTPException: If sending the message fails
    """
    try:
        logger.info(f"Received send message request for order {message_input.order_id}")

        result = client.send_message(
            order_id=message_input.order_id,
            text=message_input.text,
            attachments=message_input.attachments
        )

        logger.info(f"Successfully sent message to order {message_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to send message to order {message_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error sending message to order {message_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/files/add", response_model=Dict[str, Any])
async def add_files(
    add_files_input: AddFilesInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Add files to an order via Qualia GraphQL API.

    Args:
        add_files_input: File addition details including order_id and files object with name, base_64, and is_primary
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: Updated outstanding tasks

    Raises:
        HTTPException: If adding files fails
    """
    try:
        logger.info(f"Received add files request for order {add_files_input.order_id}")

        result = client.add_files(
            order_id=add_files_input.order_id,
            files=add_files_input.files.model_dump(exclude_none=True)
        )

        logger.info(f"Successfully added files to order {add_files_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to add files to order {add_files_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error adding files to order {add_files_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/files/remove", response_model=Dict[str, Any])
async def remove_files(
    remove_files_input: RemoveFilesInput,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Remove files from an order via Qualia GraphQL API.

    Args:
        remove_files_input: File removal details including order_id and file_ids
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: Updated order with document information and outstanding tasks

    Raises:
        HTTPException: If removing files fails
    """
    try:
        logger.info(f"Received remove files request for order {remove_files_input.order_id}")

        result = client.remove_files(
            order_id=remove_files_input.order_id,
            file_ids=remove_files_input.file_ids
        )

        logger.info(f"Successfully removed files from order {remove_files_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to remove files from order {remove_files_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error removing files from order {remove_files_input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/fulfill-title-search", response_model=Dict[str, Any])
async def fulfill_title_search(
    wrapper: FulfillTitleSearchInputWrapper,
    client: QualiaClient = Depends(get_qualia_client)
):
    """
    Fulfill title search for an order via Qualia GraphQL API.

    Args:
        wrapper: Wrapped input with order_id and form data
        client: QualiaClient instance (injected via dependency)

    Returns:
        Dict[str, Any]: Updated outstanding tasks

    Raises:
        HTTPException: If fulfilling title search fails
    """
    try:
        fulfill_input = wrapper.input
        logger.info(f"Received fulfill title search request for order {fulfill_input.order_id}")

        result = client.fulfill_title_search(
            order_id=fulfill_input.order_id,
            form=fulfill_input.form.model_dump(exclude_unset=True, exclude_none=True)
        )

        logger.info(f"Successfully fulfilled title search for order {fulfill_input.order_id}")
        return result

    except RuntimeError as e:
        logger.error(f"Failed to fulfill title search for order {wrapper.input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fulfilling title search for order {wrapper.input.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")