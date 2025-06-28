import requests
import time
import logging
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from .models import WebhookEvent, IntegrationHealth, ExternalService, DataSync

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_webhook_event(self, event_id):
    """Process webhook events asynchronously with retry logic"""
    logger.info(f"Processing webhook event - ID: {event_id}")
    
    try:
        event = WebhookEvent.objects.get(id=event_id)
        event.status = 'processing'
        event.save()
        
        logger.info(f"Webhook event processing started - ID: {event_id}, Type: {event.event_type}")
        
        # Simulate processing based on event type
        if event.event_type == 'user.created':
            result = process_user_webhook(event.payload)
        elif event.event_type == 'payment.completed':
            result = process_payment_webhook(event.payload)
        elif event.event_type == 'notification.sent':
            result = process_notification_webhook(event.payload)
        else:
            result = {'status': 'unknown_event_type'}
            logger.warning(f"Unknown event type - ID: {event_id}, Type: {event.event_type}")
        
        if result.get('status') == 'success':
            event.status = 'completed'
            event.processed_at = timezone.now()
            logger.info(f"Webhook event completed - ID: {event_id}")
        else:
            raise Exception(result.get('error', 'Processing failed'))
            
    except Exception as exc:
        event.retry_count += 1
        logger.error(f"Webhook event failed - ID: {event_id}, Retry: {event.retry_count}, Error: {str(exc)}")
        
        if event.retry_count >= event.max_retries:
            event.status = 'failed'
            event.error_message = str(exc)
            logger.error(f"Webhook event permanently failed - ID: {event_id}")
        else:
            event.status = 'retry'
            countdown = 2 ** event.retry_count * 60
            logger.info(f"Webhook event retry scheduled - ID: {event_id}, Countdown: {countdown}s")
            raise self.retry(exc=exc, countdown=countdown)
    
    event.save()

def process_user_webhook(payload):
    """Process user-related webhook events"""
    # Simulate user processing
    time.sleep(1)
    return {'status': 'success', 'message': 'User webhook processed'}

def process_payment_webhook(payload):
    """Process payment-related webhook events"""
    # Simulate payment processing
    time.sleep(1)
    return {'status': 'success', 'message': 'Payment webhook processed'}

def process_notification_webhook(payload):
    """Process notification-related webhook events"""
    # Simulate notification processing
    time.sleep(1)
    return {'status': 'success', 'message': 'Notification webhook processed'}

@shared_task
def check_integration_health():
    """Monitor health of external integrations"""
    services = ExternalService.objects.filter(is_active=True)
    logger.info(f"Health check started for {services.count()} services")
    
    for service in services:
        try:
            start_time = time.time()
            response = requests.get(f"{service.base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            health, created = IntegrationHealth.objects.get_or_create(service=service)
            
            if response.status_code == 200:
                health.status = 'healthy'
                health.response_time = response_time
                health.error_message = ''
                logger.info(f"Service healthy - {service.name}, Response time: {response_time:.2f}s")
            else:
                health.status = 'degraded'
                health.error_message = f'HTTP {response.status_code}'
                logger.warning(f"Service degraded - {service.name}, Status: {response.status_code}")
                
        except requests.RequestException as e:
            health, created = IntegrationHealth.objects.get_or_create(service=service)
            health.status = 'down'
            health.error_message = str(e)
            logger.error(f"Service down - {service.name}, Error: {str(e)}")
            
        health.save()

@shared_task
def sync_external_data(tenant_id, service_id, sync_type):
    """Sync data with external services"""
    logger.info(f"Data sync started - Tenant: {tenant_id}, Service: {service_id}, Type: {sync_type}")
    
    try:
        sync = DataSync.objects.get(tenant_id=tenant_id, service_id=service_id, sync_type=sync_type)
        sync.status = 'syncing'
        sync.save()
        
        # Simulate data sync
        service = ExternalService.objects.get(id=service_id)
        response = requests.get(f"{service.base_url}/api/data/{sync_type}")
        
        if response.status_code == 200:
            data = response.json()
            sync.records_synced = len(data.get('records', []))
            sync.status = 'synced'
            sync.last_sync = timezone.now()
            logger.info(f"Data sync completed - Records: {sync.records_synced}, Service: {service.name}")
        else:
            sync.status = 'failed'
            sync.error_message = f'HTTP {response.status_code}'
            logger.error(f"Data sync failed - Service: {service.name}, Status: {response.status_code}")
            
    except Exception as e:
        sync.status = 'failed'
        sync.error_message = str(e)
        logger.error(f"Data sync error - Service: {service_id}, Error: {str(e)}")
        
    sync.save()