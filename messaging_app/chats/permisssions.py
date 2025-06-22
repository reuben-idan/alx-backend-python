from rest_framework import permissions

class IsSelfOrReadOnly(permissions.BasePermission):
    """Only allow users to edit/delete their own user information"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
    
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsSenderOrReadOnly(permissions.BasePermission):
    """Only allow editing/deleting of your own messages"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.sender == request.user
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
class IsConversationParticipant(permissions.BasePermission):
    """Only allow interacting with conversations you're part of."""
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
    
    def has_permission(self, request, view):
        return request.user.is_authenticated