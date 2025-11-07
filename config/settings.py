# config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    STAGE: str = os.getenv("STAGE", "dev")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # Secrets
    WEBHOOK_USERNAME: str
    WEBHOOK_PASSWORD: str
    QUALIA_API_TOKEN: str
    INTERNAL_API_TOKEN: str
    INTERNAL_API_URL: str

    # AWS Resources
    S3_BUCKET: str = f"qualia-orders-{os.getenv('STAGE', 'dev')}"
    DYNAMODB_TABLE: str = f"qualia-orders-{os.getenv('STAGE', 'dev')}"
    DOWNLOAD_QUEUE_URL: str
    PROCESSING_QUEUE_URL: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Default singleton instance for backwards compatibility
settings = get_settings()