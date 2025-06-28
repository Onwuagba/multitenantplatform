from rest_framework import serializers
from .models import WebhookEvent, IntegrationHealth, DataSync, ExternalService

class ExternalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalService
        fields = ['id', 'name', 'base_url', 'is_active']

class WebhookEventSerializer(serializers.ModelSerializer):
    service = ExternalServiceSerializer(read_only=True)
    
    class Meta:
        model = WebhookEvent
        fields = ['id', 'service', 'event_type', 'payload', 'status', 'retry_count', 
                 'created_at', 'processed_at', 'error_message']

class IntegrationHealthSerializer(serializers.ModelSerializer):
    service = ExternalServiceSerializer(read_only=True)
    
    class Meta:
        model = IntegrationHealth
        fields = ['id', 'service', 'status', 'response_time', 'last_check', 'error_message']

class DataSyncSerializer(serializers.ModelSerializer):
    service = ExternalServiceSerializer(read_only=True)
    
    class Meta:
        model = DataSync
        fields = ['id', 'service', 'sync_type', 'last_sync', 'status', 
                 'records_synced', 'error_message']