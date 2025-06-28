import jwt
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import TenantUser

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get('user_id')
            tenant_id = payload.get('tenant_id')
            
            if not user_id or not tenant_id:
                logger.warning(f"Invalid token payload - Missing user_id or tenant_id")
                raise AuthenticationFailed('Invalid token payload')
                
            user = TenantUser.objects.get(id=user_id, tenant_id=tenant_id)
            
            # Ensure user belongs to current tenant
            if hasattr(request, 'tenant') and request.tenant and user.tenant != request.tenant:
                logger.warning(f"Tenant mismatch - User: {user.username}, Expected: {request.tenant.domain}, Got: {user.tenant.domain}")
                raise AuthenticationFailed('User does not belong to current tenant')
            
            logger.info(f"JWT authentication successful - User: {user.username}, Tenant: {user.tenant.domain}")
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT authentication failed - Token expired")
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            logger.warning("JWT authentication failed - Invalid token")
            raise AuthenticationFailed('Invalid token')
        except TenantUser.DoesNotExist:
            logger.warning(f"JWT authentication failed - User not found: {user_id}")
            raise AuthenticationFailed('User not found')
            
    def authenticate_header(self, request):
        return 'Bearer'