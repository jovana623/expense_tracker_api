from rest_framework import permissions
from .models import SupportThread

class CanAccessSupportThreadDetails(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user==obj.user:
                return True
            
            if request.user.is_staff:
                if obj.status==SupportThread.ThreadStatus.OPEN or \
                   obj.status==SupportThread.ThreadStatus.CLOSED:
                    return True
                if obj.status==SupportThread.ThreadStatus.IN_PROGRESS:
                    return request.user==obj.staff
            return False
        
        if request.method in ['PUT','PATCH']:
            if request.user==obj.user:
                return False
            
            if request.user.is_staff:
                if not request.data and request.method=='PATCH':
                    return True

                request_keys=set(request.data.keys())
                if request_keys=={'archived'}:
                    return True
            return False
        
        if request.method=='DELETE':
            return request.user.is_staff
        
        return False
        
    