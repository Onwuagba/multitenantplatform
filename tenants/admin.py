from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tenant, TenantUser, Organization, OrganizationMembership, AuditLog

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'user_count', 'org_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('id', 'created_at')
    
    def user_count(self, obj):
        count = obj.users.count()
        url = reverse('admin:tenants_tenantuser_changelist') + f'?tenant__id__exact={obj.id}'
        return format_html('<a href="{}">{} users</a>', url, count)
    user_count.short_description = 'Users'
    
    def org_count(self, obj):
        count = obj.organizations.count()
        url = reverse('admin:tenants_organization_changelist') + f'?tenant__id__exact={obj.id}'
        return format_html('<a href="{}">{} orgs</a>', url, count)
    org_count.short_description = 'Organizations'

@admin.register(TenantUser)
class TenantUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'tenant_link', 'role', 'is_active', 'date_joined')
    list_filter = ('tenant', 'role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Tenant Info', {'fields': ('tenant', 'role')}),
    )
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'

class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ('user', 'role', 'permissions', 'joined_at')
    readonly_fields = ('joined_at',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            # Filter users by organization's tenant
            if hasattr(request, '_obj_') and request._obj_ is not None:
                kwargs['queryset'] = TenantUser.objects.filter(tenant=request._obj_.tenant)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant_link', 'member_count', 'created_by', 'created_at')
    list_filter = ('tenant', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')
    inlines = [OrganizationMembershipInline]
    
    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'
    
    def member_count(self, obj):
        count = obj.members.count()
        return format_html('<strong>{}</strong> members', count)
    member_count.short_description = 'Members'

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'organization_link', 'role_badge', 'permissions_display', 'joined_at')
    list_filter = ('role', 'organization__tenant', 'joined_at')
    search_fields = ('user__username', 'organization__name')
    readonly_fields = ('joined_at',)
    
    def user_link(self, obj):
        url = reverse('admin:tenants_tenantuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def organization_link(self, obj):
        url = reverse('admin:tenants_organization_change', args=[obj.organization.id])
        return format_html('<a href="{}">{}</a>', url, obj.organization.name)
    organization_link.short_description = 'Organization'
    
    def role_badge(self, obj):
        colors = {'owner': 'red', 'admin': 'orange', 'member': 'blue', 'viewer': 'green'}
        color = colors.get(obj.role, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.role.upper())
    role_badge.short_description = 'Role'
    
    def permissions_display(self, obj):
        if obj.permissions:
            return ', '.join(obj.permissions)
        return 'No permissions'
    permissions_display.short_description = 'Permissions'

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'resource_type', 'user_link', 'organization_link', 'tenant_link', 'timestamp', 'ip_address')
    list_filter = ('action', 'resource_type', 'tenant', 'organization', 'timestamp')
    search_fields = ('resource_id', 'user__username', 'organization__name')
    readonly_fields = ('id', 'timestamp', 'changes_display')
    date_hierarchy = 'timestamp'
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:tenants_tenantuser_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return 'System'
    user_link.short_description = 'User'
    
    def organization_link(self, obj):
        if obj.organization:
            url = reverse('admin:tenants_organization_change', args=[obj.organization.id])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return 'N/A'
    organization_link.short_description = 'Organization'
    
    def tenant_link(self, obj):
        url = reverse('admin:tenants_tenant_change', args=[obj.tenant.id])
        return format_html('<a href="{}">{}</a>', url, obj.tenant.name)
    tenant_link.short_description = 'Tenant'
    
    def changes_display(self, obj):
        import json
        return format_html('<pre>{}</pre>', json.dumps(obj.changes, indent=2))
    changes_display.short_description = 'Changes'