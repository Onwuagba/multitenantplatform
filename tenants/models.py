from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class TenantUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        
        # For regular users, tenant is required
        if 'tenant' not in extra_fields:
            raise ValueError('Tenant is required for regular users')
            
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        # Create default tenant for superuser if none exists
        if 'tenant' not in extra_fields:
            tenant, created = Tenant.objects.get_or_create(
                domain='default',
                defaults={'name': 'Default Tenant'}
            )
            extra_fields['tenant'] = tenant
            
        return self.create_user(username, email, password, **extra_fields)

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TenantUser(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('user', 'User'),
        ('viewer', 'Viewer')
    ], default='user')
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='tenant_users',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='tenant_users',
        blank=True
    )
    
    objects = TenantUserManager()

    class Meta:
        unique_together = ('tenant', 'username')

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='organizations')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(TenantUser, through='OrganizationMembership', related_name='organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='created_organizations')

    class Meta:
        unique_together = ('tenant', 'name')

class OrganizationMembership(models.Model):
    user = models.ForeignKey(TenantUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer')
    ], default='member')
    permissions = models.JSONField(default=list)  # ['read', 'write', 'delete', 'manage_users']
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'organization')

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(TenantUser, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']