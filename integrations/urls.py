from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    webhook_receiver, WebhookEventViewSet, IntegrationHealthViewSet, 
    DataSyncViewSet, trigger_sync
)

router = DefaultRouter()
router.register(r'webhook-events', WebhookEventViewSet, basename='webhook-events')
router.register(r'health', IntegrationHealthViewSet, basename='integration-health')
router.register(r'data-sync', DataSyncViewSet, basename='data-sync')

urlpatterns = [
    path('webhooks/<str:service_name>/', webhook_receiver, name='webhook-receiver'),
    path('sync/trigger/', trigger_sync, name='trigger-sync'),
    path('', include(router.urls)),
]