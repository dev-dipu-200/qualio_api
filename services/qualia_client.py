# services/qualia_client.py
import requests
import time
import random
import logging
from requests.adapters import HTTPAdapter
from config.settings import settings
from services.graphql_queries import (
    GET_ORDER_QUERY,
    GET_ORDERS_QUERY,
    ACCEPT_ORDER_MUTATION,
    CANCEL_ORDER_MUTATION,
    DECLINE_ORDER_MUTATION,
    SUBMIT_ORDER_MUTATION,
    SEND_MESSAGE_MUTATION,
    ADD_FILE_MUTATION,
    REMOVE_FILE_MUTATION,
    FULL_FILL_TITLE_SEARCH_MUTATION
)

logger = logging.getLogger(__name__)

class QualiaClient:
    """Client for Qualia API with connection pooling and retry logic."""

    def __init__(self):
        self.base_url = "https://api.qualia.com/v1"
        self.graphql_url = "https://qa-marketplace.qualia.io/api/vendor/graphql"
        self.headers = {
            "Authorization": f"Basic {settings.QUALIA_API_TOKEN}",
            "Content-Type": "application/json"
        }
        # Connection pooling for efficiency
        self.session = requests.Session()
        # Configure connection pool
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # We handle retries manually for more control
        )
        self.session.mount('https://', adapter)
        self.session.headers.update(self.headers)

    def download_order(self, order_id: str, max_retries: int = 5):
        """Download order details from Qualia API with retry logic."""
        url = f"{self.base_url}/orders/{order_id}"
        logger.info(f"Downloading order {order_id} from Qualia API", extra={
            "order_id": order_id,
            "url": url
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.get(url, timeout=30)

                if resp.status_code == 200:
                    logger.info(f"Successfully downloaded order {order_id}", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1
                    })
                    return resp.json()

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for order {order_id}, waiting {wait:.2f}s", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for order {order_id}", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {resp.status_code} for order {order_id}, retrying in {wait}s", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for order {order_id}: {str(e)}", extra={
                    "order_id": order_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error(f"Max retries exceeded for order {order_id}", extra={
            "order_id": order_id,
            "max_retries": max_retries
        })
        raise RuntimeError(f"Max retries exceeded for order {order_id}")

    def get_orders(self, filters: dict = None, max_retries: int = 5):
        """Get list of orders via Qualia GraphQL API with retry logic.

        Args:
            filters: Optional dictionary with filters (status, customer_id, order_number, limit, offset)
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Response from the orders query
        """
        variables = {
            "input": filters if filters else {}
        }

        payload = {
            "query": GET_ORDERS_QUERY,
            "variables": variables
        }

        logger.info("Fetching orders list via Qualia GraphQL API", extra={
            "filters": filters
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.graphql_url, json=payload, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()

                    # Check for GraphQL errors
                    if "errors" in data:
                        logger.error("GraphQL errors for orders list", extra={
                            "errors": data["errors"]
                        })
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")

                    logger.info("Successfully fetched orders list", extra={
                        "attempt": attempt + 1,
                        "filters": filters
                    })
                    return data.get("data", {})

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for orders list, waiting {wait:.2f}s", extra={
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for orders list", extra={
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {resp.status_code} for orders list, retrying in {wait}s", extra={
                        "status_code": resp.status_code,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for orders list: {str(e)}", extra={
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error("Max retries exceeded for fetching orders list", extra={
            "max_retries": max_retries
        })
        raise RuntimeError("Max retries exceeded for orders list")

    def get_order(self, order_id: str, max_retries: int = 5):
        """Get order details via Qualia GraphQL API with retry logic.

        Args:
            order_id: The order ID to retrieve
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Response from the GetOrder query
        """
        variables = {
            "input": order_id
        }

        payload = {
            "query": GET_ORDER_QUERY,
            "variables": variables
        }

        logger.info(f"Fetching order {order_id} via Qualia GraphQL API", extra={
            "order_id": order_id
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.graphql_url, json=payload, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()

                    # Check for GraphQL errors
                    if "errors" in data:
                        logger.error(f"GraphQL errors for order {order_id}", extra={
                            "order_id": order_id,
                            "errors": data["errors"]
                        })
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")

                    logger.info(f"Successfully fetched order {order_id}", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1
                    })
                    return data.get("data", {})

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for order {order_id}, waiting {wait:.2f}s", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for order {order_id}", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {resp.status_code} for order {order_id}, retrying in {wait}s", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for order {order_id}: {str(e)}", extra={
                    "order_id": order_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error(f"Max retries exceeded for fetching order {order_id}", extra={
            "order_id": order_id,
            "max_retries": max_retries
        })
        raise RuntimeError(f"Max retries exceeded for order {order_id}")

    def accept_order(self, order_id: str, max_retries: int = 5):
        """Accept an order via Qualia GraphQL API with retry logic.

        Args:
            order_id: The order ID to accept
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Response from the acceptOrder mutation
        """
        variables = {
            "input": {
                "order_id": order_id
            }
        }

        payload = {
            "query": ACCEPT_ORDER_MUTATION,
            "variables": variables
        }

        logger.info(f"Accepting order {order_id} via Qualia GraphQL API", extra={
            "order_id": order_id
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.graphql_url, json=payload, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()

                    # Check for GraphQL errors
                    if "errors" in data:
                        logger.error(f"GraphQL errors for order {order_id}", extra={
                            "order_id": order_id,
                            "errors": data["errors"]
                        })
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")

                    logger.info(f"Successfully accepted order {order_id}", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1
                    })
                    return data.get("data", {})

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for order {order_id}, waiting {wait:.2f}s", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for order {order_id}", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for order {order_id}: {str(e)}", extra={
                    "order_id": order_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error(f"Max retries exceeded for accepting order {order_id}", extra={
            "order_id": order_id,
            "max_retries": max_retries
        })

    def cancel_order(self, order_id: str, cancellation_reason: str = None, max_retries: int = 5):
        """Cancel an order via Qualia GraphQL API with retry logic.

        Args:
            order_id: The order ID to cancel
            cancellation_reason: Optional reason for cancellation
            max_retries: Maximum number of retry attempts

        Returns:
            dict: Response from the cancelOrder mutation
        """
        variables = {
            "input": {
                "order_id": order_id
            }
        }

        if cancellation_reason:
            variables["input"]["cancellation_reason"] = cancellation_reason

        payload = {
            "query": CANCEL_ORDER_MUTATION,
            "variables": variables
        }

        logger.info(f"Cancelling order {order_id} via Qualia GraphQL API", extra={
            "order_id": order_id,
            "cancellation_reason": cancellation_reason
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.graphql_url, json=payload, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()

                    # Check for GraphQL errors
                    if "errors" in data:
                        logger.error(f"GraphQL errors for order {order_id}", extra={
                            "order_id": order_id,
                            "errors": data["errors"]
                        })
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")

                    logger.info(f"Successfully cancelled order {order_id}", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1
                    })
                    return data.get("data", {})

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for order {order_id}, waiting {wait:.2f}s", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for order {order_id}", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {resp.status_code} for order {order_id}, retrying in {wait}s", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for order {order_id}: {str(e)}", extra={
                    "order_id": order_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error(f"Max retries exceeded for cancelling order {order_id}", extra={
            "order_id": order_id,
            "max_retries": max_retries
        })
        raise RuntimeError(f"Max retries exceeded for order {order_id}")

    def decline_order(self, order_id: str, decline_reason: str = None, max_retries: int = 5):
        """Decline an order via Qualia GraphQL API with retry logic."""
        variables = {
            "input": {
                "order_id": order_id
            }
        }
        if decline_reason:
            variables["input"]["decline_reason"] = decline_reason

        return self._execute_mutation(
            mutation=DECLINE_ORDER_MUTATION,
            variables=variables,
            order_id=order_id,
            action="declining",
            max_retries=max_retries
        )

    def submit_order(self, order_id: str, max_retries: int = 5):
        """Submit an order via Qualia GraphQL API with retry logic."""
        variables = {
            "input": {
                "order_id": order_id
            }
        }

        return self._execute_mutation(
            mutation=SUBMIT_ORDER_MUTATION,
            variables=variables,
            order_id=order_id,
            action="submitting",
            max_retries=max_retries
        )

    def send_message(self, order_id: str, text: str, attachments: list = None, max_retries: int = 5):
        """Send a message to an order via Qualia GraphQL API with retry logic."""
        variables = {
            "input": {
                "order_id": order_id,
                "text": text
            }
        }
        if attachments:
            variables["input"]["attachments"] = attachments

        return self._execute_mutation(
            mutation=SEND_MESSAGE_MUTATION,
            variables=variables,
            order_id=order_id,
            action="sending message to",
            max_retries=max_retries
        )

    def add_files(self, order_id: str, files: dict, max_retries: int = 5):
        """Add files to an order via Qualia GraphQL API with retry logic.

        Args:
            order_id: The order ID to add files to
            files: Dictionary with 'name', 'base_64', and optional 'is_primary' keys
            max_retries: Maximum number of retry attempts
        """
        variables = {
            "input": {
                "order_id": order_id,
                "files": files
            }
        }

        return self._execute_mutation(
            mutation=ADD_FILE_MUTATION,
            variables=variables,
            order_id=order_id,
            action="adding files to",
            max_retries=max_retries
        )

    def remove_files(self, order_id: str, file_ids: list, max_retries: int = 5):
        """Remove files from an order via Qualia GraphQL API with retry logic."""
        variables = {
            "input": {
                "order_id": order_id,
                "file_ids": file_ids
            }
        }

        return self._execute_mutation(
            mutation=REMOVE_FILE_MUTATION,
            variables=variables,
            order_id=order_id,
            action="removing files from",
            max_retries=max_retries
        )

    def fulfill_title_search(self, order_id: str, form: dict, max_retries: int = 5):
        """Fulfill title search for an order via Qualia GraphQL API with retry logic."""
        variables = {
            "input": {
                "order_id": order_id,
                "form": form
            }
        }

        return self._execute_mutation(
            mutation=FULL_FILL_TITLE_SEARCH_MUTATION,
            variables=variables,
            order_id=order_id,
            action="fulfilling title search for",
            max_retries=max_retries
        )

    def _execute_mutation(self, mutation: str, variables: dict, order_id: str, action: str, max_retries: int = 5):
        """Helper method to execute GraphQL mutations with retry logic."""
        payload = {
            "query": mutation,
            "variables": variables
        }

        logger.info(f"{action.capitalize()} order {order_id} via Qualia GraphQL API", extra={
            "order_id": order_id,
            "action": action
        })

        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.graphql_url, json=payload, timeout=30)

                if resp.status_code == 200:
                    data = resp.json()

                    if "errors" in data:
                        logger.error(f"GraphQL errors for {action} order {order_id}", extra={
                            "order_id": order_id,
                            "errors": data["errors"]
                        })
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")

                    logger.info(f"Successfully {action} order {order_id}", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1
                    })
                    return data.get("data", {})

                elif resp.status_code == 429:
                    wait = (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"Rate limited for {action} order {order_id}, waiting {wait:.2f}s", extra={
                        "order_id": order_id,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)
                    continue

                elif resp.status_code in (400, 401, 403, 404):
                    logger.error(f"Permanent error {resp.status_code} for {action} order {order_id}", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "response": resp.text
                    })
                    raise RuntimeError(f"Permanent error {resp.status_code}: {resp.text}")

                else:
                    wait = 2 ** attempt
                    logger.warning(f"HTTP {resp.status_code} for {action} order {order_id}, retrying in {wait}s", extra={
                        "order_id": order_id,
                        "status_code": resp.status_code,
                        "attempt": attempt + 1,
                        "wait_seconds": wait
                    })
                    time.sleep(wait)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for {action} order {order_id}: {str(e)}", extra={
                    "order_id": order_id,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)

        logger.error(f"Max retries exceeded for {action} order {order_id}", extra={
            "order_id": order_id,
            "max_retries": max_retries
        })
        raise RuntimeError(f"Max retries exceeded for {action} order {order_id}")

    def __del__(self):
        """Close session on cleanup."""
        if hasattr(self, 'session'):
            self.session.close()