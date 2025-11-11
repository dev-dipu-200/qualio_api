# Qualia Marketplace API - Authentication Setup Guide

## Overview

The Qualia Marketplace API uses **Basic Authentication** with base64-encoded credentials. This guide covers proper authentication setup for both sandbox and production environments.

## Important: Authorization vs Authentication

⚠️ **Critical:** Use the header key **"Authorization"** (NOT "Authentication")

```python
# ✓ CORRECT
headers = {
    "Authorization": f"Basic {base64_encoded_credentials}"
}

# ✗ WRONG - Will result in 401 Unauthorized
headers = {
    "Authentication": f"Basic {base64_encoded_credentials}"
}
```

## Environments

### Sandbox Environment

**Portal URL:** https://sandbox-marketplace.qualia.io/title/manage/api

**API Endpoint:** https://sandbox-marketplace.qualia.io/api/vendor/graphql

**Use for:**
- Development and testing
- Integration testing
- Webhook testing with test orders

### Production Environment

**Portal URL:** https://marketplace.qualia.io/title/manage/api

**API Endpoint:** https://marketplace.qualia.io/api/vendor/graphql

**Use for:**
- Live customer orders
- Real order fulfillment
- Production webhooks

## Getting Your API Credentials

### Step 1: Access the Marketplace Portal

**Sandbox:**
1. Navigate to: https://sandbox-marketplace.qualia.io/title/manage/api
2. Log in with your vendor account credentials

**Production:**
1. Navigate to: https://marketplace.qualia.io/title/manage/api
2. Log in with your vendor account credentials

### Step 2: Locate API Credentials

On the **Manage > API** page, you'll find:
- **Username** - Your API username
- **Password** - Your API password (may need to generate/reveal)

⚠️ **Note:** Credentials are **different** for sandbox and production environments

### Step 3: Encode Credentials

Qualia expects a **Base64-encoded** string of `username:password`

**Example:**
```bash
# If your credentials are:
# Username: vendor_user
# Password: vendor_pass_123

# Encode them:
echo -n "vendor_user:vendor_pass_123" | base64
# Output: dmVuZG9yX3VzZXI6dmVuZG9yX3Bhc3NfMTIz
```

**In Python:**
```python
import base64

username = "vendor_user"
password = "vendor_pass_123"

credentials = f"{username}:{password}"
encoded = base64.b64encode(credentials.encode()).decode()
# Result: dmVuZG9yX3VzZXI6dmVuZG9yX3Bhc3NfMTIz
```

## Configuration in Your Application

### Environment Variables (.env file)

```env
# Qualia API Configuration
# Use sandbox for development, production for live orders
QUALIA_ENVIRONMENT=sandbox  # or 'production'

# Sandbox Credentials (from sandbox portal)
QUALIA_SANDBOX_API_TOKEN=your_base64_encoded_sandbox_token

# Production Credentials (from production portal)
QUALIA_PRODUCTION_API_TOKEN=your_base64_encoded_production_token

# Active token (will be used by the application)
QUALIA_API_TOKEN=${QUALIA_SANDBOX_API_TOKEN}  # Switch to production when ready
```

### Current Implementation Check

Your current `services/qualia_client.py` has:

```python
self.graphql_url = "https://qa-marketplace.qualia.io/api/vendor/graphql"
self.headers = {
    "Authorization": f"Basic {settings.QUALIA_API_TOKEN}",
    "Content-Type": "application/json"
}
```

**Note:** The URL shows `qa-marketplace` which appears to be a QA environment. Verify this is correct, as official docs show:
- Sandbox: `sandbox-marketplace.qualia.io`
- Production: `marketplace.qualia.io`

### Recommended Configuration Setup

**Update `config/settings.py`:**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Qualia API Configuration
    QUALIA_ENVIRONMENT: str = os.getenv("QUALIA_ENVIRONMENT", "sandbox")
    QUALIA_API_TOKEN: str = os.getenv("QUALIA_API_TOKEN")

    @property
    def qualia_graphql_url(self) -> str:
        """Get the correct GraphQL URL based on environment."""
        if self.QUALIA_ENVIRONMENT == "production":
            return "https://marketplace.qualia.io/api/vendor/graphql"
        else:
            return "https://sandbox-marketplace.qualia.io/api/vendor/graphql"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Update `services/qualia_client.py`:**

```python
def __init__(self):
    self.graphql_url = settings.qualia_graphql_url  # Dynamic based on environment
    self.headers = {
        "Authorization": f"Basic {settings.QUALIA_API_TOKEN}",
        "Content-Type": "application/json"
    }
```

## Testing Authentication

### Method 1: Simple Health Check Query

```python
import requests
import os

token = os.getenv("QUALIA_API_TOKEN")
url = "https://sandbox-marketplace.qualia.io/api/vendor/graphql"

query = """
query {
  orders(input: { limit: 1 }) {
    orders {
      _id
      order_number
    }
  }
}
"""

response = requests.post(
    url,
    json={"query": query},
    headers={
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
)

if response.status_code == 200:
    print("✓ Authentication successful!")
    print(response.json())
else:
    print(f"✗ Authentication failed: {response.status_code}")
    print(response.text)
```

### Method 2: Using Your QualiaClient

```python
from services.qualia_client import QualiaClient

client = QualiaClient()
try:
    orders = client.get_orders(filters={"limit": 1})
    print("✓ Authentication successful!")
    print(f"Found {len(orders.get('orders', {}).get('orders', []))} orders")
except Exception as e:
    print(f"✗ Authentication failed: {str(e)}")
```

### Method 3: cURL Test

```bash
# Replace YOUR_BASE64_TOKEN with your actual token
curl -X POST https://sandbox-marketplace.qualia.io/api/vendor/graphql \
  -H "Authorization: Basic YOUR_BASE64_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { orders(input: { limit: 1 }) { orders { _id order_number } } }"
  }'
```

## Common Authentication Errors

### 401 Unauthorized

**Possible causes:**
1. ❌ Using "Authentication" instead of "Authorization" header
2. ❌ Incorrect base64 encoding
3. ❌ Wrong credentials (username/password)
4. ❌ Using sandbox credentials with production endpoint (or vice versa)
5. ❌ Credentials expired or revoked

**How to fix:**
- Verify header key is "Authorization"
- Re-encode your credentials
- Get fresh credentials from Qualia portal
- Ensure environment matches credentials

### 403 Forbidden

**Possible causes:**
1. ❌ Account doesn't have API access enabled
2. ❌ Credentials don't have permission for requested operation

**How to fix:**
- Contact Qualia support to enable API access
- Verify your vendor account has proper permissions

## Security Best Practices

### ✓ DO:
- Store credentials in environment variables
- Use separate credentials for sandbox and production
- Rotate credentials periodically
- Use HTTPS for all API calls (already enforced by Qualia)
- Keep credentials out of version control

### ✗ DON'T:
- Hardcode credentials in source code
- Commit credentials to git
- Share production credentials
- Use production credentials in development
- Log full authorization headers

## Environment Switching

### For Development

```env
QUALIA_ENVIRONMENT=sandbox
QUALIA_API_TOKEN=your_sandbox_token_here
```

### For Production

```env
QUALIA_ENVIRONMENT=production
QUALIA_API_TOKEN=your_production_token_here
```

### Multiple Environment Management

**Option 1: Separate .env files**

```bash
# .env.sandbox
QUALIA_ENVIRONMENT=sandbox
QUALIA_API_TOKEN=sandbox_token

# .env.production
QUALIA_ENVIRONMENT=production
QUALIA_API_TOKEN=production_token

# Use with:
uvicorn main:app --env-file .env.sandbox
uvicorn main:app --env-file .env.production
```

**Option 2: Environment-specific variables**

```env
# Store both
QUALIA_SANDBOX_TOKEN=sandbox_token
QUALIA_PRODUCTION_TOKEN=production_token
QUALIA_ENVIRONMENT=sandbox

# In code, select based on QUALIA_ENVIRONMENT
```

## Webhook Authentication (Separate)

**Important:** The authentication discussed above is for **your application calling Qualia's API**.

Webhook authentication is **different** - it's for **Qualia calling your webhook endpoint**:

```env
# Your webhook credentials (you define these)
# Qualia will use these to authenticate TO YOU
WEBHOOK_USERNAME=your_webhook_user
WEBHOOK_PASSWORD=your_webhook_pass
```

## Verification Checklist

Before going to production:

- [ ] Sandbox authentication working
- [ ] Can fetch orders from sandbox
- [ ] Can submit test orders in sandbox
- [ ] Production credentials obtained
- [ ] Production authentication tested
- [ ] Environment variable structure configured
- [ ] Credentials secured (not in code)
- [ ] Webhook credentials registered with Qualia
- [ ] Tested end-to-end in sandbox
- [ ] Ready to switch to production

## Quick Reference

| Component | Sandbox | Production |
|-----------|---------|------------|
| **Portal** | sandbox-marketplace.qualia.io/title/manage/api | marketplace.qualia.io/title/manage/api |
| **API Endpoint** | sandbox-marketplace.qualia.io/api/vendor/graphql | marketplace.qualia.io/api/vendor/graphql |
| **Header** | Authorization: Basic {token} | Authorization: Basic {token} |
| **Credentials** | From sandbox portal | From production portal |
| **Use For** | Development, testing | Live orders |

## Getting Help

**Authentication Issues:**
- Verify credentials from Qualia portal
- Check header key is "Authorization" (not "Authentication")
- Test with cURL first to isolate issue
- Check environment matches credentials

**API Access Issues:**
- Contact Qualia support
- Verify vendor account is approved
- Check API access is enabled

**Webhook Issues:**
- Separate issue from API authentication
- Check webhook credentials match what you registered
- Verify webhook endpoint is accessible from internet

---

**Next Steps:**
1. Get credentials from Qualia portal (sandbox first)
2. Base64 encode them
3. Add to `.env` file
4. Test authentication with simple query
5. Proceed with webhook and order fulfillment setup
