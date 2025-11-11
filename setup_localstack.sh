#!/bin/bash
# setup_localstack.sh
# Script to set up LocalStack resources for development

set -e

echo "================================"
echo "LocalStack Setup Script"
echo "================================"

# Load environment variables
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
ENDPOINT_URL=http://localhost:4566
TABLE_NAME=qualia-orders-dev
BUCKET_NAME=qualia-orders-dev

echo ""
echo "Checking LocalStack connection..."
if ! curl -s $ENDPOINT_URL/_localstack/health > /dev/null; then
    echo "✗ LocalStack is not running!"
    echo ""
    echo "Please start LocalStack first:"
    echo "  docker run -d --name localstack -p 4566:4566 localstack/localstack"
    echo ""
    echo "Or if already created:"
    echo "  docker start localstack"
    exit 1
fi

echo "✓ LocalStack is running"

echo ""
echo "Creating DynamoDB Table: $TABLE_NAME"
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url $ENDPOINT_URL \
    2>/dev/null && echo "✓ Table created" || echo "⚠ Table might already exist"

echo ""
echo "Creating S3 Bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME \
    --endpoint-url $ENDPOINT_URL \
    2>/dev/null && echo "✓ Bucket created" || echo "⚠ Bucket might already exist"

echo ""
echo "Creating SQS Queues..."
aws sqs create-queue \
    --queue-name qualia-download-queue-dev \
    --endpoint-url $ENDPOINT_URL \
    > /dev/null 2>&1 && echo "✓ Download queue created" || echo "⚠ Download queue might already exist"

aws sqs create-queue \
    --queue-name qualia-processing-queue-dev \
    --endpoint-url $ENDPOINT_URL \
    > /dev/null 2>&1 && echo "✓ Processing queue created" || echo "⚠ Processing queue might already exist"

echo ""
echo "================================"
echo "Verifying Resources..."
echo "================================"

echo ""
echo "DynamoDB Tables:"
aws dynamodb list-tables --endpoint-url $ENDPOINT_URL --output table

echo ""
echo "S3 Buckets:"
aws s3 ls --endpoint-url $ENDPOINT_URL

echo ""
echo "SQS Queues:"
aws sqs list-queues --endpoint-url $ENDPOINT_URL --output table

echo ""
echo "================================"
echo "✓ Setup Complete!"
echo "================================"
echo ""
echo "You can now start your application:"
echo "  python main.py"
echo ""
echo "Or with uvicorn:"
echo "  uvicorn main:app --reload"
echo ""
