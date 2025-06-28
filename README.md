# Multi-Tenant SaaS Platform with External Integrations

A Django REST Framework project implementing a multi-tenant SaaS platform with external API integrations.

## Features

### Part A: Multi-Tenant Platform (60%)
- **Data Isolation**: Database-level tenant isolation using middleware
- **Authentication & Authorization**: JWT-based auth with role management
- **Core API Endpoints**: RESTful APIs for users and organizations
- **Audit Logging**: Complete audit trail for all data modifications
- **API Protections**: Rate limiting and input validation

### Part B: External Integration Engine (40%)
- **Webhook Handling**: Accept webhooks from multiple external services
- **Async Event Handling**: Celery-based processing with retry logic
- **External API Calls**: Robust error handling for 3rd-party services
- **Data Sync**: Keep external and internal systems synchronized
- **Health Monitoring**: Monitor integration status and report failures

## Quick Start

1. **Setup Environment**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Start Redis** (for Celery):
   ```bash
   redis-server
   ```

3. **Start Celery Worker**:
   ```bash
   source venv/bin/activate
   celery -A multitenant_platform worker --loglevel=info
   ```

4. **Start Django Server**:
   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/tenants/auth/` - Login with JWT

### Tenant Management
- `GET/POST /api/tenants/users/` - User CRUD operations
- `GET/POST /api/tenants/organizations/` - Organization management
- `GET /api/tenants/audit-logs/` - Audit trail

### Integrations
- `POST /api/integrations/webhooks/{service_name}/` - Webhook receiver
- `GET /api/integrations/webhook-events/` - Webhook event history
- `GET /api/integrations/health/` - Integration health status
- `POST /api/integrations/sync/trigger/` - Manual data sync

### Mock Services
- `GET/POST /api/mock/users/` - Mock user service
- `GET/POST /api/mock/subscriptions/` - Mock payment service
- `GET/POST /api/mock/notifications/` - Mock communication service
- `GET /api/mock/health/` - Health check endpoint

## Usage Examples

### 1. Authentication
```bash
curl -X POST http://localhost:8000/api/tenants/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password",
    "tenant_domain": "default"
  }'
```

### 2. Create User (with JWT token)
```bash
curl -X POST http://localhost:8000/api/tenants/users/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "X-Tenant-Domain: default" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "role": "user"
  }'
```

### 3. Send Webhook
```bash
curl -X POST http://localhost:8000/api/integrations/webhooks/user-service/ \
  -H "X-Event-Type: user.created" \
  -H "X-Tenant-Domain: default" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "email": "test@example.com"
  }'
```

## Architecture

### Multi-Tenant Isolation
- Tenant middleware extracts tenant context from headers/subdomain
- All database queries are automatically filtered by tenant
- JWT tokens include tenant information for security

### Async Processing
- Webhooks are processed asynchronously using Celery
- Retry logic with exponential backoff for failed tasks
- Health monitoring runs as periodic tasks

### Security Features
- JWT authentication with tenant validation
- Rate limiting on authentication endpoints
- Input validation on all API endpoints
- Audit logging for compliance

## Testing

Run the test suite:
```bash
source venv/bin/activate
python manage.py test
```

## Production Considerations

1. **Database**: Use PostgreSQL with proper indexing
2. **Redis**: Configure Redis persistence for production
3. **Security**: Use environment variables for secrets
4. **Monitoring**: Add proper logging and monitoring
5. **Scaling**: Consider database sharding for large tenant counts