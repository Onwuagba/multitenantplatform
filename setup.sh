#!/bin/bash

# Setup script for Multi-Tenant Platform

echo "Setting up Multi-Tenant Platform..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create migrations
python manage.py makemigrations tenants
python manage.py makemigrations integrations
python manage.py makemigrations mock_services

# Run migrations
python manage.py migrate

# Create superuser (optional)
echo "Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Load initial data from fixtures
if [ -f "fixtures/initial_data.json" ]; then
    echo "Loading initial data from fixtures..."
    python manage.py loaddata fixtures/initial_data.json
else
    echo "Creating initial data..."
    python manage.py shell << EOF
from tenants.models import Tenant, TenantUser
from integrations.models import ExternalService

# Create default tenant
tenant, created = Tenant.objects.get_or_create(
    domain='default',
    defaults={'name': 'Default Tenant'}
)

# Create admin user
admin_user, created = TenantUser.objects.get_or_create(
    username='admin',
    tenant=tenant,
    defaults={
        'email': 'admin@example.com',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()

# Create external services
services = [
    {'name': 'user-service', 'base_url': 'http://localhost:8000/api/mock'},
    {'name': 'payment-service', 'base_url': 'http://localhost:8000/api/mock'},
    {'name': 'communication-service', 'base_url': 'http://localhost:8000/api/mock'},
]

for service_data in services:
    ExternalService.objects.get_or_create(**service_data)

print("Initial data created!")
EOF
fi

echo "Setup completed! Run 'python manage.py runserver' to start the server."