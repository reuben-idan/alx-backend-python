# chats/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to interact with messages in that conversation.
    """

    def has_permission(self, request, view):
        # Global level: Ensure the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Object-level: Ensure the user is part of the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        elif hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        else:
            return False
