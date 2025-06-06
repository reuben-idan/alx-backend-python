# chats/permissions.py

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsParticipantOfConversation(BasePermission):
    """
    Allow only authenticated users who are participants of the conversation
    to send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        # First ensure the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Determine if user is part of the conversation
        if request.user.is_authenticated:
            user = request.user

            # Check for actions on messages
            if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                # Conversation exists directly or through related field
                if hasattr(obj, 'conversation'):
                    return user in obj.conversation.participants.all()
                elif hasattr(obj, 'participants'):
                    return user in obj.participants.all()

        return False
