#!/usr/bin/env python3
"""
Setup script for LocalStack resources
Creates DynamoDB tables, S3 buckets, and SQS queues for local development
"""
import boto3
import os
import sys
from botocore.exceptions import ClientError

# LocalStack configuration
ENDPOINT_URL = "http://localhost:4566"
REGION = "us-east-1"
TABLE_NAME = "qualia-orders-dev"
BUCKET_NAME = "qualia-orders-dev"

# Set dummy credentials for LocalStack
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

def check_localstack():
    """Check if LocalStack is running."""
    import urllib.request
    try:
        urllib.request.urlopen(f"{ENDPOINT_URL}/_localstack/health", timeout=2)
        print("✓ LocalStack is running")
        return True
    except Exception:
        print("✗ LocalStack is not running!")
        print("\nPlease start LocalStack first:")
        print("  docker run -d --name localstack -p 4566:4566 localstack/localstack")
        print("\nOr if already created:")
        print("  docker start localstack")
        return False

def create_dynamodb_table():
    """Create DynamoDB table for orders."""
    print(f"\nCreating DynamoDB Table: {TABLE_NAME}")

    dynamodb = boto3.client('dynamodb', region_name=REGION, endpoint_url=ENDPOINT_URL)

    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Table '{TABLE_NAME}' created successfully")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table '{TABLE_NAME}' already exists")
            return True
        else:
            print(f"✗ Error creating table: {e}")
            return False

def create_s3_bucket():
    """Create S3 bucket for files."""
    print(f"\nCreating S3 Bucket: {BUCKET_NAME}")

    s3 = boto3.client('s3', region_name=REGION, endpoint_url=ENDPOINT_URL)

    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"✓ Bucket '{BUCKET_NAME}' created successfully")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"⚠ Bucket '{BUCKET_NAME}' already exists")
            return True
        else:
            print(f"✗ Error creating bucket: {e}")
            return False

def create_sqs_queues():
    """Create SQS queues for processing."""
    print("\nCreating SQS Queues...")

    sqs = boto3.client('sqs', region_name=REGION, endpoint_url=ENDPOINT_URL)

    queues = [
        'qualia-download-queue-dev',
        'qualia-processing-queue-dev'
    ]

    success = True
    for queue_name in queues:
        try:
            sqs.create_queue(QueueName=queue_name)
            print(f"✓ Queue '{queue_name}' created successfully")
        except ClientError as e:
            if 'QueueAlreadyExists' in str(e):
                print(f"⚠ Queue '{queue_name}' already exists")
            else:
                print(f"✗ Error creating queue '{queue_name}': {e}")
                success = False

    return success

def verify_resources():
    """Verify all resources were created."""
    print("\n" + "="*50)
    print("Verifying Resources...")
    print("="*50)

    # Check DynamoDB
    print("\nDynamoDB Tables:")
    dynamodb = boto3.client('dynamodb', region_name=REGION, endpoint_url=ENDPOINT_URL)
    try:
        response = dynamodb.list_tables()
        for table in response['TableNames']:
            print(f"  - {table}")
    except Exception as e:
        print(f"  ✗ Error listing tables: {e}")

    # Check S3
    print("\nS3 Buckets:")
    s3 = boto3.client('s3', region_name=REGION, endpoint_url=ENDPOINT_URL)
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']}")
    except Exception as e:
        print(f"  ✗ Error listing buckets: {e}")

    # Check SQS
    print("\nSQS Queues:")
    sqs = boto3.client('sqs', region_name=REGION, endpoint_url=ENDPOINT_URL)
    try:
        response = sqs.list_queues()
        if 'QueueUrls' in response:
            for queue_url in response['QueueUrls']:
                queue_name = queue_url.split('/')[-1]
                print(f"  - {queue_name}")
    except Exception as e:
        print(f"  ✗ Error listing queues: {e}")

def main():
    """Main setup function."""
    print("="*50)
    print("LocalStack Setup Script")
    print("="*50)

    # Check if LocalStack is running
    if not check_localstack():
        sys.exit(1)

    # Create resources
    results = []
    results.append(create_dynamodb_table())
    results.append(create_s3_bucket())
    results.append(create_sqs_queues())

    # Verify resources
    verify_resources()

    # Summary
    print("\n" + "="*50)
    if all(results):
        print("✓ Setup Complete!")
    else:
        print("⚠ Setup completed with some warnings")
    print("="*50)

    print("\nYou can now start your application:")
    print("  python main.py")
    print("\nOr with uvicorn:")
    print("  uvicorn main:app --reload")
    print()

if __name__ == "__main__":
    main()
