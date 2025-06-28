import hashlib
import hmac
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import WebhookEvent, WebhookEndpoint, IntegrationHealth, DataSync, ExternalService
from .tasks import process_webhook_event, sync_external_data
from .serializers import WebhookEventSerializer, IntegrationHealthSerializer, DataSyncSerializer
from multitenant_platform.utils import success_response, error_response

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_receiver(request, service_name):
    """Receive webhooks from external services"""
    tenant_domain = request.META.get('HTTP_X_TENANT_DOMAIN')
    event_type = request.META.get('HTTP_X_EVENT_TYPE')
    ip_address = request.META.get('REMOTE_ADDR')

    logger.info(
        f"Webhook received - Service: {service_name}, Event: {event_type}, Tenant: {tenant_domain}, IP: {ip_address}")
    
    # Validate event type
    valid_event_types = [
        'user.created', 'user.updated', 'user.deleted',
        'payment.completed', 'payment.failed', 'payment.refunded',
        'notification.sent', 'notification.failed'
    ]
    
    if not event_type or event_type not in valid_event_types:
        logger.warning(f"Webhook rejected - Invalid event type: {event_type} for service: {service_name}")
        return JsonResponse({'status': 'failure', 'error': f'Invalid event type: {event_type}'}, status=400)

    try:
        # Find the service
        service = ExternalService.objects.get(
            name=service_name, is_active=True)

        # Get tenant from header
        if not tenant_domain:
            logger.warning(
                f"Webhook rejected - Missing tenant domain for service: {service_name}")
            return JsonResponse({'status': 'failure', 'error': 'Missing tenant domain'}, status=400)

        # Get webhook endpoint
        webhook_endpoint = WebhookEndpoint.objects.get(
            service=service,
            tenant__domain=tenant_domain
        )

        # Verify webhook signature
        signature = request.META.get('HTTP_X_SIGNATURE')
        if signature:
            expected_signature = hmac.new(
                webhook_endpoint.secret_key.encode(),
                request.body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(
                    f"Webhook rejected - Invalid signature for service: {service_name}, tenant: {tenant_domain}")
                return JsonResponse({'status': 'failure', 'error': 'Invalid signature'}, status=401)

        # Parse JSON payload
        import json
        try:
            payload = json.loads(request.body.decode('utf-8')) if request.body else {}
        except json.JSONDecodeError:
            payload = {}
        
        # Create webhook event
        event = WebhookEvent.objects.create(
            tenant_id=webhook_endpoint.tenant.id,
            service=service,
            event_type=event_type,
            payload=payload
        )

        logger.info(
            f"Webhook event created - ID: {event.id}, Service: {service_name}, Type: {event_type}")

        # Process asynchronously
        process_webhook_event.delay(str(event.id))

        return JsonResponse({'status': 'success', 'message': 'Webhook received', 'data': {'event_id': str(event.id)}})

    except (ExternalService.DoesNotExist, WebhookEndpoint.DoesNotExist):
        logger.error(
            f"Webhook failed - Service/endpoint not found: {service_name}, tenant: {tenant_domain}")
        return JsonResponse({'status': 'failure', 'error': 'Service not found'}, status=404)
    except Exception as e:
        logger.error(
            f"Webhook error - Service: {service_name}, Error: {str(e)}")
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WebhookEventSerializer

    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return WebhookEvent.objects.filter(tenant=self.request.tenant)
        return WebhookEvent.objects.none()


class IntegrationHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IntegrationHealthSerializer
    queryset = IntegrationHealth.objects.all()
    permission_classes = [AllowAny]


class DataSyncViewSet(viewsets.ModelViewSet):
    serializer_class = DataSyncSerializer

    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return DataSync.objects.filter(tenant=self.request.tenant)
        return DataSync.objects.none()


@api_view(['POST'])
@extend_schema(
    summary="Trigger data sync",
    description="Manually trigger data synchronization with external service",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'service_id': {'type': 'string', 'format': 'uuid'},
                'sync_type': {'type': 'string', 'enum': ['users', 'subscriptions', 'notifications']}
            },
            'required': ['service_id', 'sync_type']
        }
    }
)
def trigger_sync(request):
    """Manually trigger data sync"""
    service_id = request.data.get('service_id')
    sync_type = request.data.get('sync_type')

    logger.info(
        f"Sync trigger requested - Service: {service_id}, Type: {sync_type}, User: {request.user.username if request.user else 'Anonymous'}")

    if not all([service_id, sync_type]):
        logger.warning(
            f"Sync trigger failed - Missing parameters from user: {request.user.username if request.user else 'Anonymous'}")
        return error_response('Missing parameters')

    if hasattr(request, 'tenant') and request.tenant:
        sync_external_data.delay(
            str(request.tenant.id), service_id, sync_type)
        logger.info(
            f"Sync triggered - Tenant: {request.tenant.domain}, Service: {service_id}, Type: {sync_type}")
        return success_response(None, 'Sync triggered')

    logger.warning(
        f"Sync trigger failed - No tenant context for user: {request.user.username if request.user else 'Anonymous'}")
    return error_response('No tenant context')
