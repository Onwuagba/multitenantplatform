from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ExternalService, WebhookEndpoint, WebhookEvent, IntegrationHealth, DataSync

@admin.register(ExternalService)
class ExternalServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'health_status', 'webhook_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'base_url')
    readonly_fields = ('id',)
    
    def health_status(self, obj):
        try:
            health = obj.integrationhealth_set.first()
            if health:
                color = {'healthy': 'green', 'degraded': 'orange', 'down': 'red'}.get(health.status, 'gray')
                return format_html('<span style="color: {};">{}</span>', color, health.status.upper())
            return format_html('<span style="color: gray;">UNKNOWN</span>')
        except:
            return format_html('<span style="color: gray;">UNKNOWN</span>')
    health_status.short_description = 'Health'
    
    def webhook_count(self, obj):
        count = obj.webhookevent_set.count()
        url = reverse('admin:integrations_webhookevent_changelist') + f'?service__id__exact={obj.id}'
        return format_html('<a href="{}">{} events</a>', url, count)
    webhook_count.short_description = 'Webhook Events'

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ('service', 'tenant_link', 'endpoint_url', 'is_active', 'created_at')
    list_filter = ('service', 'tenant', 'is_active', 'created_at')
    search_fields = ('endpoint_url', 'tenant__name', 'service__name')
    readonly_fields = ('id', 'created_at')
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'service', 'tenant_link', 'status_badge', 'retry_count', 'created_at')
    list_filter = ('status', 'event_type', 'service', 'tenant', 'created_at')
    search_fields = ('event_type', 'service__name', 'tenant__name')
    readonly_fields = ('id', 'created_at', 'processed_at', 'payload_display')
    date_hierarchy = 'created_at'
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'retry': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'
    
    def payload_display(self, obj):
        import json
        return format_html('<pre>{}</pre>', json.dumps(obj.payload, indent=2))
    payload_display.short_description = 'Payload'

@admin.register(IntegrationHealth)
class IntegrationHealthAdmin(admin.ModelAdmin):
    list_display = ('service', 'status_badge', 'response_time_ms', 'last_check', 'error_summary')
    list_filter = ('status', 'service', 'last_check')
    search_fields = ('service__name', 'error_message')
    readonly_fields = ('id', 'last_check')
    
    def status_badge(self, obj):
        colors = {'healthy': 'green', 'degraded': 'orange', 'down': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'
    
    def response_time_ms(self, obj):
        if obj.response_time:
            return f"{obj.response_time * 1000:.0f}ms"
        return "N/A"
    response_time_ms.short_description = 'Response Time'
    
    def error_summary(self, obj):
        if obj.error_message:
            return obj.error_message[:50] + "..." if len(obj.error_message) > 50 else obj.error_message
        return "No errors"
    error_summary.short_description = 'Error'

@admin.register(DataSync)
class DataSyncAdmin(admin.ModelAdmin):
    list_display = ('sync_type', 'service', 'tenant_link', 'status_badge', 'records_synced', 'last_sync')
    list_filter = ('status', 'sync_type', 'service', 'tenant', 'last_sync')
    search_fields = ('sync_type', 'service__name', 'tenant__name')
    readonly_fields = ('id', 'last_sync')
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'
    
    def status_badge(self, obj):
        colors = {'synced': 'green', 'syncing': 'blue', 'failed': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'