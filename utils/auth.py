# utils/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config.settings import settings

security = HTTPBasic()

def verify_webhook_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = settings.WEBHOOK_USERNAME
    correct_password = settings.WEBHOOK_PASSWORD

    if not (credentials.username == correct_username and credentials.password == correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials