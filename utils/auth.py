# utils/auth.py
from fastapi import HTTPException, status, Header
from config.settings import settings

def verify_webhook_auth(authorization: str = Header(None)):
    """
    Verify webhook authentication using Authorization header with Basic token format.
    Expected format: Authorization: Basic <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Check if it starts with "Basic "
    if not authorization.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: 'Basic <token>'",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Extract the token
    token = authorization[6:]  # Remove "Basic " prefix

    # Compare with the expected token from settings
    expected_token = settings.WEBHOOK_TOKEN

    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True