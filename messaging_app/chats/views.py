# chats/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')

        # Filter messages for the given conversation and authenticated user
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Message.objects.none()

        if self.request.user not in conversation.participants.all():
            # Explicitly raise 403
            self.permission_denied(
                self.request,
                message="You are not a participant of this conversation.",
                code=status.HTTP_403_FORBIDDEN
            )

        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = Conversation.objects.get(id=conversation_id)

        if self.request.user not in conversation.participants.all():
            self.permission_denied(
                self.request,
                message="You cannot send messages to this conversation.",
                code=status.HTTP_403_FORBIDDEN
            )

        serializer.save(author=self.request.user, conversation=conversation)
