from rest_framework import serializers
from .models import Tenant, TenantUser, Organization, OrganizationMembership, AuditLog
from drf_spectacular.utils import extend_schema_field

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'domain', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']

class TenantUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = TenantUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = TenantUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = TenantUserSerializer(read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = ['user', 'role', 'permissions', 'joined_at']
        read_only_fields = ['joined_at']

class OrganizationSerializer(serializers.ModelSerializer):
    created_by = TenantUserSerializer(read_only=True)
    members = OrganizationMembershipSerializer(source='organizationmembership_set', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'created_at', 'created_by', 'members', 'member_count']
        read_only_fields = ['id', 'created_at', 'created_by']
    
    @extend_schema_field(int)
    def get_member_count(self, obj):
        return obj.members.count()

class AuditLogSerializer(serializers.ModelSerializer):
    user = TenantUserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'resource_type', 'resource_id', 'changes', 'timestamp', 'ip_address']
        read_only_fields = ['id', 'timestamp']