from rest_framework.permissions import BasePermission

class OrganizationPermission(BasePermission):
    """Check organization-level permissions"""
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'tenant'):
            return False
            
        # Check if user is member of organization
        try:
            membership = obj.organizationmembership_set.get(user=request.user)
            
            # Permission mapping
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return 'read' in membership.permissions or membership.role in ['owner', 'admin', 'member']
            elif request.method in ['POST', 'PUT', 'PATCH']:
                return 'write' in membership.permissions or membership.role in ['owner', 'admin']
            elif request.method == 'DELETE':
                return 'delete' in membership.permissions or membership.role == 'owner'
            
        except:
            return False
        
        return False