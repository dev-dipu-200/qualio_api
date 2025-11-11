# AWS Configuration Guide

## The Issue

You're seeing this error:
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

This happens because the application needs AWS credentials to access DynamoDB, S3, and SQS.

## Your Current Setup

Looking at your `.env` file, you're using **LocalStack** for local development:
- SQS queues point to `localhost:4566`
- This is a local AWS emulator for development

## Solutions

### Option 1: Local Development with LocalStack (Recommended for Development)

LocalStack emulates AWS services locally. You need to:

#### 1. Install LocalStack

```bash
# Using pip
pip install localstack

# Or using Docker (recommended)
docker run -d \
  --name localstack \
  -p 4566:4566 \
  -p 4571:4571 \
  -e SERVICES=dynamodb,s3,sqs \
  localstack/localstack
```

#### 2. Configure AWS Credentials for LocalStack

LocalStack accepts any credentials, but they must be set:

**Add to your `.env` file:**
```env
# AWS Credentials (for LocalStack - use dummy values)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1

# LocalStack endpoint
LOCALSTACK_ENDPOINT=http://localhost:4566
USE_LOCALSTACK=true
```

**Or set as environment variables:**
```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

#### 3. Create LocalStack Resources

```bash
# DynamoDB Table
aws dynamodb create-table \
    --table-name qualia-orders-dev \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:4566

# S3 Bucket
aws s3 mb s3://qualia-orders-dev \
    --endpoint-url http://localhost:4566

# SQS Queues
aws sqs create-queue \
    --queue-name qualia-download-queue-dev \
    --endpoint-url http://localhost:4566

aws sqs create-queue \
    --queue-name qualia-processing-queue-dev \
    --endpoint-url http://localhost:4566
```

### Option 2: Use AWS Credentials File (For Both Local and Production)

#### 1. Configure AWS CLI

```bash
aws configure
```

Enter:
- **AWS Access Key ID:** Your actual AWS key (or "test" for LocalStack)
- **AWS Secret Access Key:** Your actual secret (or "test" for LocalStack)
- **Default region:** us-east-1
- **Default output format:** json

This creates `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_KEY_ID
aws_secret_access_key = YOUR_SECRET_KEY
```

#### 2. For LocalStack, Point to Local Endpoint

Update `services/dynamodb_service.py` to support LocalStack:

```python
import boto3
import os

# Check if using LocalStack
if os.getenv('USE_LOCALSTACK', 'false').lower() == 'true':
    endpoint_url = os.getenv('LOCALSTACK_ENDPOINT', 'http://localhost:4566')
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=settings.AWS_REGION,
        endpoint_url=endpoint_url
    )
else:
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
```

### Option 3: Environment Variables (Quick Fix)

Add directly to your shell or `.env`:

```bash
# Add to .env file
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Or export in terminal
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

### Option 4: Disable DynamoDB for Testing (Temporary)

If you just want to test the webhook without AWS:

Create a mock DynamoDB service:

```python
# services/dynamodb_mock.py
import logging

logger = logging.getLogger(__name__)

def store_activity(activity_data: dict):
    """Mock store activity - just log it."""
    logger.info(f"[MOCK] Would store activity: {activity_data}")
    return True

def store_message(message_data: dict):
    """Mock store message - just log it."""
    logger.info(f"[MOCK] Would store message: {message_data}")
    return True

def get_messages_by_order(order_id: str, message_type: str = None):
    """Mock get messages - return empty list."""
    logger.info(f"[MOCK] Would fetch messages for order: {order_id}")
    return []
```

Then conditionally import in your handler based on environment.

## Recommended Solution for You

Based on your LocalStack setup, here's what I recommend:

### Step 1: Update `.env` File

```env
# .env
STAGE=dev
AWS_REGION=us-east-1

# AWS Credentials (LocalStack accepts any values)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# LocalStack Configuration
USE_LOCALSTACK=true
LOCALSTACK_ENDPOINT=http://localhost:4566

# Webhook Auth
WEBHOOK_USERNAME=mtx
WEBHOOK_PASSWORD=YHeiedyKXxAnw9XXc3T0eQ3joJkz3DS3zrKBqitxvZk
QUALIA_API_TOKEN='bXR4OllIZWllZHlLWHhBbnc5WFhjM1QwZVEzam9Ka3ozRFMzenJLQnFpdHh2Wms='
INTERNAL_API_TOKEN=internal-secret
INTERNAL_API_URL='http://localhost:8000/'

# LocalStack SQS URLs
DOWNLOAD_QUEUE_URL=http://localhost:4566/000000000000/qualia-download-queue-dev
PROCESSING_QUEUE_URL=http://localhost:4566/000000000000/qualia-processing-queue-dev
```

### Step 2: Update DynamoDB Service to Support LocalStack

I'll create an updated version of the DynamoDB service.

### Step 3: Start LocalStack and Create Resources

```bash
# Start LocalStack (if not running)
docker start localstack

# Or if not installed:
docker run -d --name localstack -p 4566:4566 localstack/localstack

# Create DynamoDB table
aws dynamodb create-table \
    --table-name qualia-orders-dev \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:4566
```

## Verification

After setup, verify it works:

```python
# test_aws_connection.py
import boto3
import os

# Set credentials if not in environment
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

# Test DynamoDB connection
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    endpoint_url='http://localhost:4566'
)

try:
    # List tables
    tables = list(dynamodb.tables.all())
    print(f"✓ Connected to DynamoDB")
    print(f"  Tables: {[t.name for t in tables]}")
except Exception as e:
    print(f"✗ Connection failed: {str(e)}")
```

## Production Setup

For production (real AWS):

### 1. Create Real AWS Resources

```bash
# Use AWS Console or CLI (without --endpoint-url)
aws dynamodb create-table \
    --table-name qualia-orders-prod \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### 2. Use IAM Credentials

Either:
- **IAM Role** (recommended for EC2/ECS/Lambda)
- **IAM User** with access keys

### 3. Update .env for Production

```env
STAGE=prod
USE_LOCALSTACK=false
# Remove LOCALSTACK_ENDPOINT

# Real AWS credentials
AWS_ACCESS_KEY_ID=your_real_key
AWS_SECRET_ACCESS_KEY=your_real_secret
AWS_REGION=us-east-1
```

## Quick Fix Right Now

Run this in your terminal before starting the app:

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Then start your app
python main.py
```

This will allow the app to connect to LocalStack's DynamoDB.
