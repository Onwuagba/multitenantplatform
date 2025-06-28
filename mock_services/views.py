import requests
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import MockUser, MockSubscription, MockNotification
from .serializers import MockUserSerializer, MockSubscriptionSerializer, MockNotificationSerializer
from multitenant_platform.utils import success_response, error_response

logger = logging.getLogger(__name__)

# Mock User Management Service
class MockUserViewSet(viewsets.ModelViewSet):
    queryset = MockUser.objects.all()
    serializer_class = MockUserSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"Mock user created - ID: {user.id}, Email: {user.email}")
        
        # Send webhook to main platform
        self.send_webhook('user.created', {
            'user_id': str(user.id),
            'email': user.email,
            'name': user.name,
            'status': user.status
        })
    
    def send_webhook(self, event_type, data):
        webhook_url = 'http://localhost:8000/api/integrations/webhooks/user-service/'
        payload = {
            'event_type': event_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        try:
            response = requests.post(webhook_url, json=payload, headers={
                'X-Event-Type': event_type,
                'X-Tenant-Domain': 'default'
            })
            logger.info(f"Webhook sent - Event: {event_type}, Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook failed - Event: {event_type}, Error: {str(e)}")

# Mock Payment Service
class MockSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = MockSubscription.objects.all()
    serializer_class = MockSubscriptionSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        subscription = serializer.save()
        logger.info(f"Mock subscription created - ID: {subscription.id}, Plan: {subscription.plan}, Amount: {subscription.amount}")
        
        # Send webhook for payment completed
        self.send_webhook('payment.completed', {
            'subscription_id': str(subscription.id),
            'user_id': str(subscription.user.id),
            'plan': subscription.plan,
            'amount': str(subscription.amount),
            'status': subscription.status
        })
    
    def send_webhook(self, event_type, data):
        webhook_url = 'http://localhost:8000/api/integrations/webhooks/payment-service/'
        payload = {
            'event_type': event_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        try:
            requests.post(webhook_url, json=payload, headers={
                'X-Event-Type': event_type,
                'X-Tenant-Domain': 'default'
            })
        except:
            pass

# Mock Communication Service
class MockNotificationViewSet(viewsets.ModelViewSet):
    queryset = MockNotification.objects.all()
    serializer_class = MockNotificationSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        notification = serializer.save()
        logger.info(f"Mock notification created - ID: {notification.id}, Type: {notification.type}, Subject: {notification.subject}")
        
        # Simulate sending notification
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        # Send webhook for notification sent
        self.send_webhook('notification.sent', {
            'notification_id': str(notification.id),
            'user_id': str(notification.user.id),
            'type': notification.type,
            'subject': notification.subject,
            'status': notification.status
        })
    
    def send_webhook(self, event_type, data):
        webhook_url = 'http://localhost:8000/api/integrations/webhooks/communication-service/'
        payload = {
            'event_type': event_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        try:
            requests.post(webhook_url, json=payload, headers={
                'X-Event-Type': event_type,
                'X-Tenant-Domain': 'default'
            })
        except:
            pass

@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="Health check",
    description="Check the health status of mock services"
)
def health_check(request):
    """Health check endpoint for integration monitoring"""
    logger.info("Health check requested")
    return success_response({
        'timestamp': timezone.now().isoformat(),
        'services': {
            'user_service': 'operational',
            'payment_service': 'operational',
            'communication_service': 'operational'
        }
    }, 'System healthy')

@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="Get mock data",
    description="Retrieve mock data for synchronization",
    parameters=[
        {'name': 'data_type', 'in': 'path', 'required': True, 'schema': {'type': 'string', 'enum': ['users', 'subscriptions', 'notifications']}}
    ]
)
def mock_data_endpoint(request, data_type):
    """Mock data endpoint for sync operations"""
    logger.info(f"Data sync requested - Type: {data_type}")
    
    if data_type == 'users':
        users = MockUser.objects.all()[:10]
        logger.info(f"Returning {users.count()} users for sync")
        return success_response({
            'records': MockUserSerializer(users, many=True).data,
            'total': users.count()
        })
    elif data_type == 'subscriptions':
        subscriptions = MockSubscription.objects.all()[:10]
        logger.info(f"Returning {subscriptions.count()} subscriptions for sync")
        return success_response({
            'records': MockSubscriptionSerializer(subscriptions, many=True).data,
            'total': subscriptions.count()
        })
    elif data_type == 'notifications':
        notifications = MockNotification.objects.all()[:10]
        logger.info(f"Returning {notifications.count()} notifications for sync")
        return success_response({
            'records': MockNotificationSerializer(notifications, many=True).data,
            'total': notifications.count()
        })
    else:
        logger.warning(f"Invalid data type requested: {data_type}")
        return error_response('Invalid data type')