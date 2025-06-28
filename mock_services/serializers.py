from rest_framework import serializers
from .models import MockUser, MockSubscription, MockNotification

class MockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockUser
        fields = ['id', 'email', 'name', 'status', 'created_at']

class MockSubscriptionSerializer(serializers.ModelSerializer):
    user = MockUserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MockSubscription
        fields = ['id', 'user', 'user_id', 'plan', 'status', 'amount', 'created_at']

class MockNotificationSerializer(serializers.ModelSerializer):
    user = MockUserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MockNotification
        fields = ['id', 'user', 'user_id', 'type', 'subject', 'message', 'status', 'created_at', 'sent_at']