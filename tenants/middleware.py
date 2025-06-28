import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant

logger = logging.getLogger(__name__)

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract tenant from subdomain or header
        host = request.get_host().split(':')[0]
        
        # Try to get tenant from X-Tenant-Domain header first
        tenant_domain = request.META.get('HTTP_X_TENANT_DOMAIN')
        
        if not tenant_domain:
            # Extract from subdomain
            parts = host.split('.')
            if len(parts) > 2:
                tenant_domain = parts[0]
            else:
                tenant_domain = 'default'
        
        try:
            tenant = Tenant.objects.get(domain=tenant_domain, is_active=True)
            request.tenant = tenant
            logger.info(f"Tenant resolved - Domain: {tenant_domain}, Host: {host}")
        except Tenant.DoesNotExist:
            request.tenant = None
            logger.warning(f"Tenant not found - Domain: {tenant_domain}, Host: {host}")
            
        return None