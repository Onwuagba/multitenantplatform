from django.contrib import admin
from django.utils.html import format_html
from .models import MockUser, MockSubscription, MockNotification

@admin.register(MockUser)
class MockUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'status_badge', 'subscription_count', 'notification_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('id', 'created_at')
    
    def status_badge(self, obj):
        colors = {'active': 'green', 'inactive': 'orange', 'suspended': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'
    
    def subscription_count(self, obj):
        return obj.subscriptions.count()
    subscription_count.short_description = 'Subscriptions'
    
    def notification_count(self, obj):
        return obj.notifications.count()
    notification_count.short_description = 'Notifications'

@admin.register(MockSubscription)
class MockSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'plan', 'amount', 'status_badge', 'created_at')
    list_filter = ('plan', 'status', 'created_at')
    search_fields = ('user__email', 'user__name')
    readonly_fields = ('id', 'created_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def status_badge(self, obj):
        colors = {'active': 'green', 'cancelled': 'orange', 'expired': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'

@admin.register(MockNotification)
class MockNotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user_email', 'type', 'status_badge', 'created_at', 'sent_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('subject', 'user__email', 'message')
    readonly_fields = ('id', 'created_at', 'sent_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def status_badge(self, obj):
        colors = {'pending': 'orange', 'sent': 'green', 'failed': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'