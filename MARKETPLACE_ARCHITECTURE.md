# Qualia Marketplace API - Architecture Overview

## Understanding Qualia Marketplace

Qualia Marketplace is a platform where vendors offer products to title agents, settlement agents, and real estate attorneys. The Marketplace Vendor API enables vendors to interact programmatically with orders without using the UI.

## Two Main Interaction Channels

### 1. Order Fulfillment (GraphQL API)
- View orders
- Fulfill orders with product-specific data
- Submit completed orders
- Manage order lifecycle

### 2. Activity Notifications (Webhooks)
- Real-time notifications of order activity
- Message notifications
- Document updates
- Order status changes

**Our Implementation:** This codebase focuses on **Activity Notifications** (webhooks) with automatic order data fetching.

## Product Verticals

Qualia Marketplace products are categorized into **Product Verticals**. Each vertical has specific data requirements and fulfillment mutations.

### Supported Verticals

| Vertical | Description | Example Products |
|----------|-------------|------------------|
| **Title** | Title searches, commitments, policies | Title Search Plus, Title Commitment |
| **Notary** | Notary services | Mobile Notary, RON (Remote Online Notary) |
| **Survey** | Property surveys | ALTA Survey, Boundary Survey |
| **ReleaseTracking** | Lien and mortgage release tracking | Mortgage Release Tracking |
| **Other** | Miscellaneous services | HOA Documents, Municipal Lien Search |

### How Verticals Work with GraphQL

Each product vertical corresponds to a **GraphQL Fragment** that extends the base order schema with vertical-specific data.

**Example - Base Order Query:**
```graphql
query GetOrder($input: ID!) {
  order(_id: $input) {
    order {
      _id
      order_number
      status
      # ... base fields

      # Vertical-specific fragments
      ...TitleFields      # Only populated for Title products
      ...NotaryFields     # Only populated for Notary products
      ...SurveyFields     # Only populated for Survey products
    }
  }
}
```

## Product-Specific Fulfill Mutations

Different products require different fulfillment mutations based on their data needs:

### Title Vertical
```graphql
mutation fulfillTitleSearchPlus($input: TitleSearchPlusInput) {
  fulfillTitleSearchPlus(input: $input) {
    outstanding_tasks
  }
}
```

### Survey Vertical
```graphql
mutation fulfillSurvey($input: SurveyInput) {
  fulfillSurvey(input: $input) {
    outstanding_tasks
  }
}
```

### Generic Document Upload
```graphql
mutation addFiles($input: AddFilesInput) {
  addFiles(input: $input) {
    outstanding_tasks
  }
}
```

## Determining Your Development Needs

### Step 1: Identify Your Products
List the specific products/services your organization will provide on Marketplace.

**Example:**
- Title Search Plus ✓
- Title Commitment ✓
- Mobile Notary ✓

### Step 2: Identify Required Fragments
Determine which GraphQL fragments you need to query order data.

**Example:**
- Products: Title Search Plus → Fragment: `...TitleFields`
- Products: Mobile Notary → Fragment: `...NotaryFields`

### Step 3: Identify Required Mutations
Map your products to the fulfillment mutations you'll use.

**Example:**
- Title Search Plus → `fulfillTitleSearchPlus()`
- Mobile Notary → `addFiles()` or vertical-specific mutation

## How This Implementation Fits

### Webhook Flow
```
1. Customer places order in Qualia
   ↓
2. Qualia sends webhook: order_request
   ↓
3. YOUR WEBHOOK receives notification
   ↓
4. Store activity in DynamoDB
   ↓
5. Fetch full order details using GraphQL
   (with appropriate fragments for product vertical)
   ↓
6. Process order based on product type
   ↓
7. Fulfill order using appropriate mutation
   ↓
8. Submit completed order
```

### Your Current Implementation

**✓ Webhook Reception** - Handles all activity notifications
**✓ Activity Storage** - Stores all activity types in DynamoDB
**✓ Order Fetching** - Can fetch full order details via GraphQL
**⚡ Next Step** - Add product vertical detection and routing

## Implementing Product Vertical Support

### 1. Detect Product Vertical from Order

When you receive an `order_request` activity:

```python
# Fetch full order details
order = qualia_client.get_order(order_id)

# Check product vertical
product_type = order.get('order', {}).get('product_type')
vertical = order.get('order', {}).get('vertical')

# Route to appropriate handler
if vertical == 'Title':
    handle_title_order(order)
elif vertical == 'Notary':
    handle_notary_order(order)
# ... etc
```

### 2. Query with Appropriate Fragments

Modify your GraphQL query to include vertical-specific fragments:

```python
GET_ORDER_WITH_TITLE_FIELDS = """
query GetOrder($input: ID!) {
  order(_id: $input) {
    order {
      # Base fields
      _id
      order_number

      # Title-specific fields
      ...TitleFields
    }
  }
}

fragment TitleFields on Order {
  title_search_results
  title_exceptions
  # ... other title fields
}
"""
```

### 3. Use Appropriate Fulfill Mutation

Based on product type, call the correct fulfillment mutation:

```python
if product_type == 'title_search_plus':
    qualia_client.fulfill_title_search(
        order_id=order_id,
        form={
            # Title search results
        }
    )
```

## Implementation Recommendations

### For Starting Out

1. **Focus on Your Verticals**
   - Implement only the product verticals you offer
   - Don't build unused fragments/mutations

2. **Start with Order Request Webhook**
   - When `order_request` activity arrives
   - Fetch full order details
   - Store in your system
   - Process according to product type

3. **Implement Fulfillment Gradually**
   - Start with one product type
   - Build the fulfillment mutation for it
   - Test end-to-end
   - Add more products incrementally

### Development Workflow

```
Phase 1: Webhook Reception (✓ Already Done)
├── Receive all activity notifications
├── Store in DynamoDB
└── Fetch order details when needed

Phase 2: Order Processing (Next Step)
├── Detect product vertical
├── Extract vertical-specific data
├── Route to appropriate handler
└── Store structured data

Phase 3: Fulfillment (Future)
├── Implement vertical-specific mutations
├── Build data transformation logic
├── Submit completed orders
└── Handle order lifecycle

Phase 4: Optimization
├── Add retry logic
├── Implement error recovery
├── Add monitoring/alerts
└── Build admin dashboard
```

## Example: Title Search Plus Order Flow

### 1. Receive Webhook
```json
POST /webhook/activity
{
  "description": "You've received an order for a Title Search Plus...",
  "type": "order_request",
  "order_id": "bK8bg5tajNkDpDk25"
}
```

### 2. Fetch Order Details
```python
order = qualia_client.get_order("bK8bg5tajNkDpDk25")
# Returns order with Title vertical fields
```

### 3. Extract Title-Specific Data
```python
properties = order['order']['properties']
borrowers = order['order']['borrowers']
product_type = order['order']['product_type']  # "title_search_plus"
```

### 4. Process Order
```python
# Your business logic
title_results = perform_title_search(properties, borrowers)
```

### 5. Fulfill Order
```python
qualia_client.fulfill_title_search(
    order_id="bK8bg5tajNkDpDk25",
    form={
        "search_results": title_results,
        # ... other required fields
    }
)
```

### 6. Submit Order
```python
qualia_client.submit_order("bK8bg5tajNkDpDk25")
```

## Your Current Codebase Status

### ✓ Implemented
- Webhook endpoint for all activity types
- Activity storage in DynamoDB
- Order fetching via GraphQL
- Message detail fetching
- Basic authentication
- Comprehensive logging

### 🔄 Partially Implemented
- Order query (base fields only, no vertical fragments)
- Generic mutations (addFiles, removeFiles, sendMessage)

### ⏳ Not Yet Implemented
- Product vertical detection
- Vertical-specific GraphQL fragments
- Vertical-specific fulfillment mutations
- Order routing based on product type
- Business logic for order processing

## Next Steps Recommendations

### Immediate (Required for Production)
1. **Identify Your Product Verticals**
   - List specific products you'll offer
   - Document required data for each

2. **Add Vertical Detection**
   - When order_request webhook arrives
   - Fetch order and detect vertical
   - Store vertical info with activity

3. **Implement Primary Fulfillment**
   - Start with your most common product
   - Add the specific fulfill mutation
   - Test end-to-end workflow

### Short-term (First Month)
1. Add vertical-specific fragments to order queries
2. Implement fulfillment for all your product types
3. Add order lifecycle management
4. Build retry and error handling

### Long-term (Ongoing)
1. Build admin dashboard
2. Add analytics and reporting
3. Optimize performance
4. Add automation where possible

## Resources

- **Qualia GraphQL Playground:** Use to explore available fragments
- **Marketplace UI:** Reference for understanding order flow
- **This Codebase:** Solid foundation for webhooks and basic queries

---

**Key Takeaway:** Your webhook implementation is complete and production-ready. The next phase is adding product vertical support and fulfillment logic specific to the products you offer on Qualia Marketplace.
