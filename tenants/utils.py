import logging
from .models import AuditLog

logger = logging.getLogger(__name__)

def log_audit(tenant, user, action, resource_type, resource_id, changes, ip_address=None):
    """Log audit trail for tenant operations"""
    try:
        # Hide sensitive data from changes
        safe_changes = sanitize_data(changes)
        
        AuditLog.objects.create(
            tenant=tenant,
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=safe_changes,
            ip_address=ip_address
        )
        
        logger.info(f"Audit log created - Tenant: {tenant.domain}, User: {user.username if user else 'System'}, "
                   f"Action: {action}, Resource: {resource_type}:{resource_id}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")

def sanitize_data(data):
    """Remove sensitive data from logs"""
    if not isinstance(data, dict):
        return data
    
    sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
    sanitized = {}
    
    for key, value in data.items():
        if any(field in key.lower() for field in sensitive_fields):
            sanitized[key] = '***HIDDEN***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_data(value)
        else:
            sanitized[key] = value
    
    return sanitized