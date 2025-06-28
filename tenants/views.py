import jwt
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tenant, TenantUser, Organization, AuditLog
from .serializers import TenantUserSerializer, OrganizationSerializer, AuditLogSerializer
from .utils import log_audit, sanitize_data
from multitenant_platform.utils import success_response, error_response

logger = logging.getLogger(__name__)

class AuthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User Authentication",
        description="Authenticate user and return JWT token",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                    'tenant_domain': {'type': 'string'}
                },
                'required': ['username', 'password', 'tenant_domain']
            }
        },
        responses={200: {'description': 'Authentication successful'}}
    )
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        tenant_domain = request.data.get('tenant_domain')
        ip_address = request.META.get('REMOTE_ADDR')
        
        logger.info(f"Login attempt - Username: {username}, Tenant: {tenant_domain}, IP: {ip_address}")
        
        if not all([username, password, tenant_domain]):
            logger.warning(f"Login failed - Missing credentials from IP: {ip_address}")
            return error_response('Missing credentials')
            
        try:
            tenant = Tenant.objects.get(domain=tenant_domain, is_active=True)
            user = TenantUser.objects.get(username=username, tenant=tenant)
            
            if user.check_password(password) and user.is_active:
                payload = {
                    'user_id': user.id,
                    'tenant_id': str(tenant.id),
                    'role': user.role,
                    'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_DELTA)
                }
                token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
                
                log_audit(tenant, user, 'LOGIN', 'USER', str(user.id), {}, ip_address)
                logger.info(f"Login successful - User: {username}, Tenant: {tenant_domain}")
                
                return success_response({
                    'token': token,
                    'user': TenantUserSerializer(user).data
                }, 'Login successful')
            else:
                logger.warning(f"Login failed - Invalid password for user: {username}, tenant: {tenant_domain}")
                return error_response('Invalid credentials', status.HTTP_401_UNAUTHORIZED)
                
        except (Tenant.DoesNotExist, TenantUser.DoesNotExist):
            logger.warning(f"Login failed - User/tenant not found: {username}@{tenant_domain}")
            return error_response('Invalid credentials', status.HTTP_401_UNAUTHORIZED)

class TenantUserViewSet(viewsets.ModelViewSet):
    serializer_class = TenantUserSerializer
    
    @extend_schema(
        summary="List tenant users",
        description="Get all users for the current tenant",
        parameters=[
            OpenApiParameter('X-Tenant-Domain', str, OpenApiParameter.HEADER, description='Tenant domain')
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create tenant user",
        description="Create a new user for the current tenant"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return TenantUser.objects.filter(tenant=self.request.tenant)
        return TenantUser.objects.none()
    
    def perform_create(self, serializer):
        user = serializer.save(tenant=self.request.tenant)
        safe_data = sanitize_data(serializer.validated_data)
        log_audit(self.request.tenant, self.request.user, 'CREATE', 'USER', str(user.id), 
                 safe_data, self.request.META.get('REMOTE_ADDR'))
        logger.info(f"User created - ID: {user.id}, Username: {user.username}, Tenant: {self.request.tenant.domain}")

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    
    @extend_schema(
        summary="List organizations",
        description="Get all organizations for the current tenant"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create organization",
        description="Create a new organization for the current tenant"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Organization.objects.filter(tenant=self.request.tenant)
        return Organization.objects.none()
    
    def perform_create(self, serializer):
        org = serializer.save(tenant=self.request.tenant, created_by=self.request.user)
        log_audit(self.request.tenant, self.request.user, 'CREATE', 'ORGANIZATION', str(org.id), 
                 serializer.validated_data, self.request.META.get('REMOTE_ADDR'))
        logger.info(f"Organization created - ID: {org.id}, Name: {org.name}, Tenant: {self.request.tenant.domain}")

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List audit logs",
        description="Get audit trail for the current tenant"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            logger.info(f"Audit logs accessed by user: {self.request.user.username}, tenant: {self.request.tenant.domain}")
            return AuditLog.objects.filter(tenant=self.request.tenant)
        logger.warning("Audit logs access attempted without tenant context")
        return AuditLog.objects.none()