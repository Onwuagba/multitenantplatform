from django.db import models
from tenants.models import Tenant
import uuid

class ExternalService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class WebhookEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='webhook_endpoints')
    service = models.ForeignKey(ExternalService, on_delete=models.CASCADE)
    endpoint_url = models.CharField(max_length=200)
    secret_key = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='webhook_events')
    service = models.ForeignKey(ExternalService, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retry', 'Retry')
    ], default='pending')
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

class IntegrationHealth(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(ExternalService, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('down', 'Down')
    ], default='healthy')
    response_time = models.FloatField(null=True, blank=True)
    last_check = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True)

class DataSync(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='data_syncs')
    service = models.ForeignKey(ExternalService, on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=50)
    last_sync = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('synced', 'Synced'),
        ('syncing', 'Syncing'),
        ('failed', 'Failed')
    ], default='synced')
    records_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)