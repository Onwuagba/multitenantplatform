# API Documentation

## Authentication

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <jwt_token>
X-Tenant-Domain: <tenant_domain>
```

## Response Format

All responses follow this format:
```json
{
  "status": "success|failure",
  "message": "Success message",
  "data": {...},
  "error": "Error message (only on failure)"
}
```

---

## Tenant Management Endpoints

### 1. Authentication
**POST** `/api/tenants/auth/`

**Request:**
```json
{
  "username": "admin",
  "password": "admin123",
  "tenant_domain": "default"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
}
```

### 2. User Management
**GET** `/api/tenants/users/`
- Lists all users for current tenant
- Requires authentication

**POST** `/api/tenants/users/`

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_active": true
  }
}
```

**GET** `/api/tenants/users/{id}/`
- Get specific user details

**PUT** `/api/tenants/users/{id}/`
- Update user (same request format as POST)

**DELETE** `/api/tenants/users/{id}/`
- Delete user

### 3. Organization Management
**GET** `/api/tenants/organizations/`
- Lists all organizations for current tenant

**POST** `/api/tenants/organizations/`

**Request:**
```json
{
  "name": "My Organization",
  "description": "Organization description"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "id": "uuid",
    "name": "My Organization",
    "description": "Organization description",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": {
      "id": 1,
      "username": "admin"
    }
  }
}
```

**GET** `/api/tenants/organizations/{id}/`
**PUT** `/api/tenants/organizations/{id}/`
**DELETE** `/api/tenants/organizations/{id}/`

### 4. Audit Logs
**GET** `/api/tenants/audit-logs/`

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "results": [
      {
        "id": "uuid",
        "user": {
          "username": "admin"
        },
        "action": "CREATE",
        "resource_type": "USER",
        "resource_id": "2",
        "changes": {...},
        "timestamp": "2024-01-15T10:30:00Z",
        "ip_address": "127.0.0.1"
      }
    ]
  }
}
```

---

## Integration Endpoints

### 1. Webhook Receiver
**POST** `/api/integrations/webhooks/{service_name}/`

**Headers:**
```
X-Event-Type: user.created
X-Tenant-Domain: default
X-Signature: sha256_signature (optional)
```

**Request:**
```json
{
  "user_id": "123",
  "email": "test@example.com",
  "name": "Test User"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook received",
  "data": {
    "event_id": "uuid"
  }
}
```

### 2. Webhook Events
**GET** `/api/integrations/webhook-events/`

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "results": [
      {
        "id": "uuid",
        "service": {
          "name": "user-service",
          "base_url": "http://localhost:8000/api/mock"
        },
        "event_type": "user.created",
        "payload": {...},
        "status": "completed",
        "retry_count": 0,
        "created_at": "2024-01-15T10:30:00Z",
        "processed_at": "2024-01-15T10:30:05Z"
      }
    ]
  }
}
```

### 3. Integration Health
**GET** `/api/integrations/health/`

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "results": [
      {
        "id": "uuid",
        "service": {
          "name": "user-service"
        },
        "status": "healthy",
        "response_time": 0.15,
        "last_check": "2024-01-15T10:30:00Z",
        "error_message": ""
      }
    ]
  }
}
```

### 4. Data Sync
**GET** `/api/integrations/data-sync/`
- Lists sync status for current tenant

**POST** `/api/integrations/sync/trigger/`

**Request:**
```json
{
  "service_id": "uuid",
  "sync_type": "users"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Sync triggered",
  "data": null
}
```

---

## Mock Services Endpoints

### 1. Mock Users
**GET** `/api/mock/users/`
**POST** `/api/mock/users/`

**Request:**
```json
{
  "email": "test@example.com",
  "name": "Test User",
  "status": "active"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "id": "uuid",
    "email": "test@example.com",
    "name": "Test User",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. Mock Subscriptions
**GET** `/api/mock/subscriptions/`
**POST** `/api/mock/subscriptions/`

**Request:**
```json
{
  "user_id": "uuid",
  "plan": "premium",
  "amount": "29.99",
  "status": "active"
}
```

### 3. Mock Notifications
**GET** `/api/mock/notifications/`
**POST** `/api/mock/notifications/`

**Request:**
```json
{
  "user_id": "uuid",
  "type": "email",
  "subject": "Welcome!",
  "message": "Welcome to our platform"
}
```

### 4. Health Check
**GET** `/api/mock/health/`

**Response:**
```json
{
  "status": "success",
  "message": "System healthy",
  "data": {
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
      "user_service": "operational",
      "payment_service": "operational",
      "communication_service": "operational"
    }
  }
}
```

### 5. Data Sync Endpoint
**GET** `/api/mock/api/data/{data_type}/`

Where `data_type` can be: `users`, `subscriptions`, `notifications`

**Response:**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "records": [...],
    "total": 10
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "failure",
  "error": "Error description",
  "data": null
}
```

Common HTTP status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## Testing Examples

### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/tenants/auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123", "tenant_domain": "default"}'
```

### 2. Create User
```bash
curl -X POST http://localhost:8000/api/tenants/users/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-Tenant-Domain: default" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 3. Send Webhook
```bash
curl -X POST http://localhost:8000/api/integrations/webhooks/user-service/ \
  -H "X-Event-Type: user.created" \
  -H "X-Tenant-Domain: default" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "email": "test@example.com"}'
```