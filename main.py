# main.py
import uvicorn
import logging
from fastapi import FastAPI
from mangum import Mangum
from handlers.webhook_handler import router as webhook_router
from routers.order import router as order_router

# Configure logging for Lambda/CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Qualia Marketplace Webhook",
    version="1.0.0",
    description="Decoupled webhook integration with claim-check and ACL"
)

# Health check endpoint with more details
@app.get("/health", tags=['Home'])
async def health():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "qualia-webhook-api",
        "version": "1.0.0"
    }

# Include webhook routes
app.include_router(webhook_router, prefix="/webhook", tags=["Webhook"])
app.include_router(order_router.router)

# Lambda handler
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, log_level="info", reload=True)