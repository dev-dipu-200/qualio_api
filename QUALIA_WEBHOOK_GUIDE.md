# Qualia Marketplace Activity Webhook Implementation

## Overview

This implementation provides a webhook endpoint to receive **Qualia Marketplace Activity Notifications** and store them in DynamoDB. The system matches Qualia's official webhook format and handles all activity types.

## Qualia Marketplace Webhook Format

Qualia sends activity notifications as JSON HTTP POST requests (no GraphQL). All activities follow a consistent structure:

```json
{
  "description": "Human-readable description",
  "type": "activity_type",
  "order_id": "order_identifier",
  "message_id": "optional_message_id"
}
```

## Supported Activity Types

### 1. `order_request`
New order received from a customer.

**Example Payload:**
```json
{
  "description": "You've received an order for a Title Search Plus in San Francisco ...",
  "type": "order_request",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

### 2. `order_cancelled`
Customer cancelled an order.

**Example Payload:**
```json
{
  "description": "Boston Legal has cancelled order #TEST-2018-1.",
  "type": "order_cancelled",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

### 3. `order_completed`
Customer accepted/completed an order.

**Example Payload:**
```json
{
  "description": "Boston Legal has accepted order #TEST-2018-1.",
  "type": "order_completed",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

### 4. `order_revision_requested`
Customer requested changes to an order.

**Example Payload:**
```json
{
  "description": "Boston Legal has requested a change on order #TEST-2018-1.",
  "type": "order_revision_requested",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

### 5. `message`
New message received (includes `message_id`).

**Example Payload:**
```json
{
  "description": "Marty McFly sent you a message.",
  "type": "message",
  "order_id": "bK8bg5tajNkDpDk25",
  "message_id": "LEPAjMB43myH8aGcP"
}
```

### 6. `documents`
New documents added to an order.

**Example Payload:**
```json
{
  "description": "Boston Legal has sent you additional documents on order #TEST-2018-1",
  "type": "documents",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

## API Endpoint

### Receive Activity Webhook

**Endpoint:** `POST /webhook/activity`

**Authentication:** HTTP Basic Auth

**Request Body:** See activity types above

**Response (Success - 200 OK):**
```json
{
  "status": "success",
  "message": "Activity message received and processed",
  "order_id": "bK8bg5tajNkDpDk25",
  "activity_type": "message",
  "request_id": "a1b2c3d4",
  "response_time_ms": 45.23
}
```

**Response (Error - 400/422):**
```json
{
  "detail": [
    {
      "loc": ["body", "type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

## Special Handling for Message Activities

When a `message` activity is received:

1. The activity notification is stored in DynamoDB
2. The system **automatically fetches** the full message details from Qualia's GraphQL API
3. The complete message (with text, attachments, etc.) is stored separately

This ensures you have both:
- The notification event (lightweight)
- The full message content (detailed)

## Data Storage

### DynamoDB Schema

#### Activity Notifications

**Keys:**
- **PK (Partition Key):** `ACTIVITY#{order_id}`
- **SK (Sort Key):** `{activity_type}#{timestamp_ms}`

**Attributes:**
| Field | Type | Description |
|-------|------|-------------|
| PK | String | `ACTIVITY#{order_id}` |
| SK | String | `{activity_type}#{timestamp}` |
| orderId | String | Order identifier |
| activityType | String | Type of activity |
| description | String | Human-readable description |
| timestamp | Number | Unix timestamp (ms) |
| receivedAt | String | ISO 8601 timestamp |
| messageId | String | Message ID (optional, for message type) |

#### Message Details (for `message` type)

**Keys:**
- **PK (Partition Key):** `MESSAGE#{order_id}`
- **SK (Sort Key):** `message#{message_id}`

**Attributes:**
| Field | Type | Description |
|-------|------|-------------|
| PK | String | `MESSAGE#{order_id}` |
| SK | String | `message#{message_id}` |
| orderId | String | Order identifier |
| messageId | String | Message identifier |
| messageType | String | "message" |
| fromName | String | Sender name |
| text | String | Message content |
| createdDate | String | ISO 8601 timestamp |
| read | Boolean | Read status |
| timestamp | Number | Unix timestamp (ms) |
| storedAt | String | ISO 8601 timestamp |
| orderNumber | String | Order number (optional) |
| attachments | List | Attachment objects (optional) |

## Setup with Qualia

### 1. Register Your Webhook in Qualia

1. Log in to Qualia Marketplace
2. Navigate to **Manage > API**
3. Click **"Add Webhook"**
4. Enter your endpoint URL: `https://your-domain.com/webhook/activity`
5. Enter your webhook credentials (username and password)

### 2. Test Your Endpoint

Use Qualia's **"Fire Test Event"** button to send a test payload to verify your endpoint is working.

### 3. Enable Webhook Retries (Optional)

Contact Qualia support to enable webhook retry logic once you've confirmed your endpoint returns correct HTTP status codes:
- **200 OK** for successful processing
- **4xx** for validation errors (bad request)
- **5xx** for server errors (triggers retry)

## Testing

### Using the Test Script

```bash
# Make sure your server is running
python main.py  # or uvicorn main:app --reload

# In another terminal, run the test
python test_qualia_webhook.py
```

The test script will:
1. Test all 6 activity types
2. Verify validation error handling
3. Display results summary

### Manual Testing with cURL

**Test order request:**
```bash
curl -X POST http://localhost:8000/webhook/activity \
  -H "Content-Type: application/json" \
  -u webhook_user:webhook_pass \
  -d '{
    "description": "Test order request",
    "type": "order_request",
    "order_id": "TEST-001"
  }'
```

**Test message notification:**
```bash
curl -X POST http://localhost:8000/webhook/activity \
  -H "Content-Type: application/json" \
  -u webhook_user:webhook_pass \
  -d '{
    "description": "John Doe sent you a message",
    "type": "message",
    "order_id": "TEST-001",
    "message_id": "MSG-001"
  }'
```

## Configuration

### Environment Variables

Required in `.env` file:

```env
# Webhook Authentication
WEBHOOK_USERNAME=your_webhook_username
WEBHOOK_PASSWORD=your_webhook_password

# Qualia API (for fetching full message details)
QUALIA_API_TOKEN=your_qualia_api_token

# AWS Configuration
AWS_REGION=us-east-1
DYNAMODB_TABLE=your_table_name
```

### DynamoDB Table Requirements

The table must support composite keys:
- **Partition Key:** `PK` (String)
- **Sort Key:** `SK` (String)

This single table stores both activities and messages using different key patterns.

## HTTP Response Codes

The webhook endpoint returns appropriate HTTP status codes for Qualia's retry logic:

| Code | Meaning | Retry? |
|------|---------|--------|
| 200 | Success - activity processed | No |
| 400 | Bad request - invalid JSON | No |
| 401 | Unauthorized - bad credentials | No |
| 422 | Validation error - invalid data | No |
| 500 | Server error - database issue | Yes |
| 503 | Service unavailable | Yes |

## Architecture Highlights

### Fast Response Times
- Webhook responds quickly (<50ms typical)
- Message fetching happens after acknowledgment
- Errors in message fetching don't fail the webhook

### Reliable Storage
- Activities stored immediately
- Composite keys enable efficient queries
- Separate storage for notifications vs. full messages

### Comprehensive Logging
All activities logged with context:
```json
{
  "timestamp": "2025-11-11T10:30:00Z",
  "level": "INFO",
  "order_id": "bK8bg5tajNkDpDk25",
  "activity_type": "message",
  "request_id": "a1b2c3d4",
  "response_time_ms": 45.23
}
```

## Workflow Example

When Qualia sends a message notification:

```
1. POST /webhook/activity
   ↓
2. Validate request (auth + payload)
   ↓
3. Store activity in DynamoDB
   ↓
4. Return 200 OK immediately
   ↓
5. [Background] Fetch full message from Qualia API
   ↓
6. [Background] Store complete message details
   ↓
7. Log success/errors
```

## Querying Data

### Get All Activities for an Order

```python
from services.dynamodb_service import table

response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'ACTIVITY#bK8bg5tajNkDpDk25'
    }
)
```

### Get Only Message Activities

```python
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': 'ACTIVITY#bK8bg5tajNkDpDk25',
        ':sk': 'message#'
    }
)
```

### Get Full Message Details

```python
response = table.query(
    KeyConditionExpression='PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'MESSAGE#bK8bg5tajNkDpDk25'
    }
)
```

## Security

- **Authentication:** HTTP Basic Auth required on all webhook endpoints
- **Validation:** Pydantic models validate all incoming data
- **Authorization:** Only valid activity types accepted
- **Error Handling:** No sensitive data exposed in error responses
- **Credentials:** Stored in environment variables, never in code

## Troubleshooting

### Common Issues

**1. "401 Unauthorized"**
- Check webhook credentials in `.env` match what you configured in Qualia
- Verify `WEBHOOK_USERNAME` and `WEBHOOK_PASSWORD` are set

**2. "422 Validation Error"**
- Verify the `type` field is one of the 6 supported activity types
- Ensure `order_id` is not empty
- Check JSON format is valid

**3. "500 Server Error"**
- Check DynamoDB table exists and is accessible
- Verify AWS credentials are configured correctly
- Review CloudWatch logs for details

**4. Message Details Not Stored**
- Verify `QUALIA_API_TOKEN` is set correctly
- Check Qualia API connectivity
- Review logs for message fetching errors (webhook will still succeed)

### Debugging Tips

1. **Check Logs:** Review application logs for detailed error information
2. **Test Locally:** Use `test_qualia_webhook.py` to verify functionality
3. **Verify Setup:** Run `verify_setup.py` to check all components
4. **Use Test Event:** Use Qualia's "Fire Test Event" button to send real payloads

## Production Considerations

### Performance
- Expected response time: <50ms for webhook acknowledgment
- Message fetching: Async, doesn't block webhook response
- DynamoDB throughput: Configure based on expected webhook volume

### Monitoring
- Track response times
- Monitor failed webhook attempts
- Alert on repeated 5xx errors
- Track message fetch failures

### Scaling
- FastAPI handles concurrent webhooks well
- DynamoDB auto-scales with demand
- Consider API Gateway + Lambda for serverless deployment

## Next Steps

After setup:
1. ✓ Deploy webhook endpoint
2. ✓ Register with Qualia
3. ✓ Test with "Fire Test Event"
4. ✓ Monitor initial webhook events
5. ✓ Request webhook retry enablement from Qualia
6. Build business logic on top of stored activities

## Support

For issues:
- Check CloudWatch logs for detailed errors
- Review DynamoDB table data
- Verify Qualia API connectivity
- Test with provided test scripts
- Contact Qualia support for webhook-related issues
