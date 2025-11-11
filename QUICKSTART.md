# Quick Start Guide

## Prerequisites

✅ Python 3.8+ installed
✅ LocalStack running (for development)
✅ Virtual environment activated

## Step 1: LocalStack Setup

### Start LocalStack (if not running)

```bash
docker run -d --name localstack -p 4566:4566 localstack/localstack
```

Or if already created:
```bash
docker start localstack
```

### Create Resources

```bash
python setup_localstack.py
```

Expected output:
```
✓ LocalStack is running
✓ Table 'qualia-orders-dev' created successfully
✓ Bucket 'qualia-orders-dev' created successfully
✓ Setup Complete!
```

## Step 2: Verify Setup

```bash
python verify_setup.py
```

Expected output:
```
✓ All verifications passed! Ready to run the application.
```

## Step 3: Start the Application

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or production mode
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test the Webhook

### Option 1: Quick Test with cURL

```bash
curl -X POST http://localhost:8000/webhook/activity \
  -H "Content-Type: application/json" \
  -u mtx:YHeiedyKXxAnw9XXc3T0eQ3joJkz3DS3zrKBqitxvZk \
  -d '{
    "description": "Test message",
    "type": "message",
    "order_id": "TEST-001",
    "message_id": "MSG-001"
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Activity message received and processed",
  "order_id": "TEST-001",
  "activity_type": "message",
  "request_id": "a1b2c3d4",
  "response_time_ms": 45.23
}
```

### Option 2: Comprehensive Test Suite

```bash
python test_qualia_webhook.py
```

This tests all 6 activity types:
- order_request
- order_cancelled
- order_completed
- order_revision_requested
- message
- documents

## Step 5: View API Documentation

Open your browser to:
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Troubleshooting

### LocalStack Not Running

```bash
# Check if running
docker ps | grep localstack

# Start if not running
docker start localstack

# Or create new container
docker run -d --name localstack -p 4566:4566 localstack/localstack
```

### AWS Credentials Error

The `.env` file should have:
```env
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
USE_LOCALSTACK=true
LOCALSTACK_ENDPOINT=http://localhost:4566
```

### Import Errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep -E "fastapi|pydantic|boto3"
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or use different port
uvicorn main:app --reload --port 8001
```

## Environment Variables

Your `.env` file should contain:

```env
# Environment
STAGE=dev
AWS_REGION=us-east-1

# AWS Credentials (LocalStack)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# LocalStack
USE_LOCALSTACK=true
LOCALSTACK_ENDPOINT=http://localhost:4566

# Webhook Auth
WEBHOOK_USERNAME=mtx
WEBHOOK_PASSWORD=YHeiedyKXxAnw9XXc3T0eQ3joJkz3DS3zrKBqitxvZk

# Qualia API
QUALIA_API_TOKEN='bXR4OllIZWllZHlLWHhBbnc5WFhjM1QwZVEzam9Ka3ozRFMzenJLQnFpdHh2Wms='

# Internal API
INTERNAL_API_TOKEN=internal-secret
INTERNAL_API_URL='http://localhost:8000/'

# SQS
DOWNLOAD_QUEUE_URL=http://localhost:4566/000000000000/qualia-download-queue-dev
PROCESSING_QUEUE_URL=http://localhost:4566/000000000000/qualia-processing-queue-dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/webhook/activity` | Receive Qualia activity webhooks |
| GET | `/webhook/activity/{order_id}` | Get messages for an order |
| GET | `/docs` | Interactive API documentation |

## Next Steps

### For Development

1. ✅ LocalStack running
2. ✅ Application running
3. ✅ Webhooks tested locally
4. ⏭️ Register webhook with Qualia (sandbox)
5. ⏭️ Test with real Qualia events
6. ⏭️ Implement order fulfillment logic

### For Production Deployment

1. Create real AWS resources (DynamoDB, S3, SQS)
2. Update `.env` with production credentials
3. Set `USE_LOCALSTACK=false`
4. Deploy to your hosting platform
5. Register webhook with Qualia (production)
6. Enable webhook retries with Qualia

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Setup LocalStack resources
python setup_localstack.py

# Verify everything is working
python verify_setup.py

# Start application (development)
uvicorn main:app --reload

# Run tests
python test_qualia_webhook.py

# Check logs
tail -f logs/app.log  # if logging to file

# Stop application
Ctrl+C
```

## Documentation Files

- **`QUICKSTART.md`** (this file) - Quick setup guide
- **`QUALIA_WEBHOOK_GUIDE.md`** - Complete webhook documentation
- **`AUTHENTICATION_SETUP.md`** - Authentication and credentials
- **`MARKETPLACE_ARCHITECTURE.md`** - Product verticals and architecture
- **`AWS_SETUP.md`** - AWS and LocalStack configuration
- **`IMPLEMENTATION_SUMMARY.md`** - Feature overview and status

## Getting Help

**Setup Issues:**
1. Run `python verify_setup.py`
2. Check LocalStack is running: `docker ps | grep localstack`
3. Verify `.env` file has all required variables
4. Check Python version: `python --version`

**Runtime Issues:**
1. Check application logs
2. Verify DynamoDB table exists in LocalStack
3. Test with simple cURL request
4. Check AWS credentials are set

**Need More Help?**
- Review the detailed documentation in `QUALIA_WEBHOOK_GUIDE.md`
- Check AWS setup in `AWS_SETUP.md`
- Review authentication setup in `AUTHENTICATION_SETUP.md`

---

**Ready?** Run `python verify_setup.py` and then `uvicorn main:app --reload` 🚀
