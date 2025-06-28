from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MockUserViewSet, MockSubscriptionViewSet, MockNotificationViewSet, health_check, mock_data_endpoint

router = DefaultRouter()
router.register(r'users', MockUserViewSet, basename='mock-users')
router.register(r'subscriptions', MockSubscriptionViewSet, basename='mock-subscriptions')
router.register(r'notifications', MockNotificationViewSet, basename='mock-notifications')

urlpatterns = [
    path('health/', health_check, name='mock-health'),
    path('api/data/<str:data_type>/', mock_data_endpoint, name='mock-data'),
    path('', include(router.urls)),
]