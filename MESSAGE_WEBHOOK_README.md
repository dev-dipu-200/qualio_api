# Qualia Message Webhook Implementation

## Overview

This implementation provides a webhook endpoint to receive Qualia messages and store them in DynamoDB based on message type. The system supports both received and sent messages with full attachment support.

## Architecture

### Components

1. **Message Webhook Model** (`models/message_webhook.py`)
   - Defines the structure for incoming message webhooks
   - Validates message data including order IDs and timestamps
   - Supports two message types: `message.received` and `message.sent`

2. **DynamoDB Service** (`services/dynamodb_service.py`)
   - `store_message()`: Stores messages in DynamoDB with composite keys
   - `get_messages_by_order()`: Retrieves messages for a specific order with optional type filtering

3. **Message Webhook Handler** (`handlers/message_webhook_handler.py`)
   - POST endpoint: Receives and stores message webhooks
   - GET endpoint: Retrieves stored messages for an order

## API Endpoints

### 1. Receive Message Webhook

**Endpoint:** `POST /webhook/messages`

**Authentication:** HTTP Basic Auth

**Request Body:**
```json
{
  "order_id": "QO-123456",
  "message_id": "MSG-001",
  "order_number": "ORD-2025-001",
  "from_name": "John Smith",
  "text": "Message content here",
  "created_date": "2025-10-28T10:30:00Z",
  "read": false,
  "attachments": [
    {
      "_id": "ATT-001",
      "name": "document.pdf",
      "url": "https://example.com/files/document.pdf",
      "tag": "contract"
    }
  ],
  "message_type": "message.received",
  "timestamp": "2025-10-28T10:30:00Z"
}
```

**Response:**
```json
{
  "message": "Message received and stored successfully",
  "order_id": "QO-123456",
  "message_id": "MSG-001",
  "message_type": "message.received",
  "request_id": "a1b2c3d4",
  "response_time_ms": 45.23
}
```

### 2. Retrieve Messages

**Endpoint:** `GET /webhook/messages/{order_id}`

**Query Parameters:**
- `message_type` (optional): Filter by message type (`message.received` or `message.sent`)

**Authentication:** HTTP Basic Auth

**Response:**
```json
{
  "order_id": "QO-123456",
  "message_type": null,
  "count": 2,
  "messages": [
    {
      "PK": "MESSAGE#QO-123456",
      "SK": "message.received#MSG-001",
      "orderId": "QO-123456",
      "messageId": "MSG-001",
      "messageType": "message.received",
      "fromName": "John Smith",
      "text": "Message content here",
      "createdDate": "2025-10-28T10:30:00Z",
      "read": false,
      "timestamp": 1730115000000,
      "storedAt": "2025-10-28T10:30:05Z",
      "orderNumber": "ORD-2025-001",
      "attachments": [...]
    }
  ]
}
```

## Data Storage

### DynamoDB Schema

Messages are stored with the following composite key structure:

- **PK (Partition Key):** `MESSAGE#{order_id}`
- **SK (Sort Key):** `{message_type}#{message_id}`

This design allows for:
- Efficient querying of all messages for an order
- Filtering by message type
- Unique identification of each message

### Stored Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| PK | String | Partition key: `MESSAGE#{order_id}` |
| SK | String | Sort key: `{message_type}#{message_id}` |
| orderId | String | Order ID (e.g., QO-123456) |
| messageId | String | Unique message identifier |
| messageType | String | Type of message (message.received or message.sent) |
| fromName | String | Name of message sender |
| text | String | Message content |
| createdDate | String | ISO 8601 timestamp when message was created |
| read | Boolean | Whether message has been read |
| timestamp | Number | Unix timestamp in milliseconds |
| storedAt | String | ISO 8601 timestamp when stored in DB |
| orderNumber | String | Order number (optional) |
| attachments | List | List of attachment objects (optional) |

## Message Types

### 1. message.received
Messages received from Qualia customers or other external parties.

### 2. message.sent
Messages sent by your system to Qualia or customers.

## Testing

### Using the Test Script

Run the provided test script to verify the implementation:

```bash
python test_message_webhook.py
```

**Before running:**
1. Ensure your FastAPI server is running: `uvicorn main:app --reload`
2. Update the AUTH credentials in `test_message_webhook.py` to match your `.env` settings
3. Ensure DynamoDB is properly configured

The test script will:
1. Send a received message webhook
2. Send a sent message webhook
3. Retrieve all messages for an order
4. Filter messages by type

### Manual Testing with cURL

**Send a message webhook:**
```bash
curl -X POST http://localhost:8000/webhook/messages \
  -H "Content-Type: application/json" \
  -u webhook_user:webhook_pass \
  -d '{
    "order_id": "QO-123456",
    "message_id": "MSG-001",
    "from_name": "John Smith",
    "text": "Test message",
    "created_date": "2025-10-28T10:30:00Z",
    "read": false,
    "message_type": "message.received",
    "timestamp": "2025-10-28T10:30:00Z"
  }'
```

**Retrieve messages:**
```bash
curl -X GET http://localhost:8000/webhook/messages/QO-123456 \
  -u webhook_user:webhook_pass
```

**Retrieve only received messages:**
```bash
curl -X GET "http://localhost:8000/webhook/messages/QO-123456?message_type=message.received" \
  -u webhook_user:webhook_pass
```

## Configuration

### Environment Variables

Ensure these variables are set in your `.env` file:

```env
# Webhook Authentication
WEBHOOK_USERNAME=your_webhook_username
WEBHOOK_PASSWORD=your_webhook_password

# AWS Configuration
AWS_REGION=us-east-1
DYNAMODB_TABLE=your_table_name
```

### DynamoDB Table Setup

The table should support composite keys:
- Partition Key: `PK` (String)
- Sort Key: `SK` (String)

## Error Handling

The webhook implements comprehensive error handling:

- **Validation Errors (400):** Invalid request format or data
- **Authentication Errors (401):** Invalid credentials
- **Server Errors (500):** Database or internal server issues

All errors are logged with detailed context for debugging.

## Logging

The system logs:
- Incoming webhook requests with metadata
- Message storage operations
- Response times
- Errors with full stack traces

Log format includes:
```json
{
  "timestamp": "2025-10-28T10:30:00Z",
  "level": "INFO",
  "order_id": "QO-123456",
  "message_id": "MSG-001",
  "message_type": "message.received",
  "request_id": "a1b2c3d4",
  "response_time_ms": 45.23
}
```

## Security

- **Authentication:** HTTP Basic Auth on all endpoints
- **Validation:** Pydantic models validate all incoming data
- **Authorization:** Webhook credentials are environment-based
- **Error Messages:** No sensitive data exposed in error responses

## Performance

- Fast response times (<50ms typical)
- Connection pooling for DynamoDB
- Efficient composite key queries
- Minimal processing overhead

## Integration with Qualia

To configure Qualia to send message webhooks to your endpoint:

1. Contact Qualia support to register your webhook endpoint
2. Provide endpoint URL: `https://your-domain.com/webhook/messages`
3. Provide webhook credentials for authentication
4. Specify which message events you want to receive:
   - `message.received`: When messages are received
   - `message.sent`: When messages are sent

## Future Enhancements

Potential improvements:
- Message search by text content
- Bulk message retrieval with pagination
- Message read status updates
- Attachment download endpoints
- Message threading support
- Real-time notifications via WebSocket

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Verify webhook credentials in `.env`
   - Ensure credentials match in test scripts

2. **500 Server Error**
   - Check DynamoDB table exists and is accessible
   - Verify AWS credentials are configured
   - Check CloudWatch logs for details

3. **Validation Errors**
   - Ensure order_id starts with "QO-"
   - Verify timestamps are in ISO 8601 format
   - Check message_type is valid

## Support

For issues or questions:
- Check application logs in CloudWatch
- Review DynamoDB table configuration
- Verify webhook authentication settings
- Test with provided test script first
