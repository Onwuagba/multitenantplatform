from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthView, TenantUserViewSet, OrganizationViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'users', TenantUserViewSet, basename='users')
router.register(r'organizations', OrganizationViewSet, basename='organizations')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('', include(router.urls)),
]