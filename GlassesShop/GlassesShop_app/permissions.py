from rest_framework import permissions
from .GetUserBySessionId import getUserBySessionId

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user and (user.is_staff or user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user and user.is_superuser)
    
class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        if (user and user.is_authenticated):
            return True
        else:
            return False
    
class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user) or request.method in permissions.SAFE_METHODS