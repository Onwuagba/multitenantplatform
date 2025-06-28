from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from tenants.models import Tenant, TenantUser, AuditLog
from integrations.models import WebhookEvent, IntegrationHealth
from mock_services.models import MockUser, MockSubscription

class MultiTenantAdminSite(AdminSite):
    site_header = "Multi-Tenant Platform Administration"
    site_title = "Platform Admin"
    index_title = "System Overview"
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Dashboard statistics
        extra_context.update({
            'tenant_count': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(is_active=True).count(),
            'total_users': TenantUser.objects.count(),
            'recent_webhooks': WebhookEvent.objects.order_by('-created_at')[:5],
            'health_status': IntegrationHealth.objects.all(),
            'recent_audits': AuditLog.objects.order_by('-timestamp')[:10],
            'mock_users': MockUser.objects.count(),
            'mock_subscriptions': MockSubscription.objects.count(),
        })
        
        return super().index(request, extra_context)

# Replace default admin site
admin_site = MultiTenantAdminSite(name='admin')

# Register all models with the custom admin site
from tenants.admin import TenantAdmin, TenantUserAdmin, OrganizationAdmin, OrganizationMembershipAdmin, AuditLogAdmin
from integrations.admin import (ExternalServiceAdmin, WebhookEndpointAdmin, 
                               WebhookEventAdmin, IntegrationHealthAdmin, DataSyncAdmin)
from mock_services.admin import MockUserAdmin, MockSubscriptionAdmin, MockNotificationAdmin

from tenants.models import Tenant, TenantUser, Organization, OrganizationMembership, AuditLog
from integrations.models import ExternalService, WebhookEndpoint, WebhookEvent, IntegrationHealth, DataSync
from mock_services.models import MockUser, MockSubscription, MockNotification

admin_site.register(Tenant, TenantAdmin)
admin_site.register(TenantUser, TenantUserAdmin)
admin_site.register(Organization, OrganizationAdmin)
admin_site.register(OrganizationMembership, OrganizationMembershipAdmin)
admin_site.register(AuditLog, AuditLogAdmin)
admin_site.register(ExternalService, ExternalServiceAdmin)
admin_site.register(WebhookEndpoint, WebhookEndpointAdmin)
admin_site.register(WebhookEvent, WebhookEventAdmin)
admin_site.register(IntegrationHealth, IntegrationHealthAdmin)
admin_site.register(DataSync, DataSyncAdmin)
admin_site.register(MockUser, MockUserAdmin)
admin_site.register(MockSubscription, MockSubscriptionAdmin)
admin_site.register(MockNotification, MockNotificationAdmin)