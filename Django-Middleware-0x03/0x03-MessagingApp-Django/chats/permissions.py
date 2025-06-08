from rest_framework.permissions import BasePermission

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants to view message object
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False