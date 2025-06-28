"""Views for the user, conversation and messages"""
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .models import User, Message, Conversation
from .permisssions import IsConversationParticipant, IsSelfOrReadOnly, IsSenderOrReadOnly


class UserView(viewsets.ModelViewSet):
    """Allow creating, retrieving, updating and deleting a user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrReadOnly,]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]        
        return [permissions.IsAuthenticated(), IsSelfOrReadOnly()]
    
    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied("Logged in users cannot create new account. Log out first.")
        return super().create(request, *args, **kwargs)


class MessageView(viewsets.ModelViewSet):
    """Allow creating, updating and deleting user messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSenderOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sender', 'sent_at']
    search_fields = ['message_body']

    def get_queryset(self):
        conversation_pk = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, pk=conversation_pk)

        if self.request.user in conversation.participants.all():
            return Message.objects.filter(conversation_id = conversation)
        raise PermissionDenied("You cannot view messages in this conversation.")

    def perform_create(self, serializer):
        sender = self.request.user
        conversation_pk = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(Conversation, pk = conversation_pk)
        return serializer.save(sender = sender, conversation = conversation)

class ConversationView(viewsets.ModelViewSet):
    """Allow users to create, update and delete conversations they are part of."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def perform_create(self, serializer):
        """Save the conversation and automatically add
        the requesting user as a participant."""
        conversation = serializer.save()
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)
    
    def get_queryset(self):
        """Only return conversations where the request user is a participant."""
        return Conversation.objects.filter(participants = self.request.user)
    
    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request, pk=None):
        conversation = self.get_object()

        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a member in this conversation.")
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status = status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, pk=user_id)

        if user in conversation.participants.all():
            return Response({"message": "User already exists in conversation."}, status=status.HTTP_200_OK)

        conversation.participants.add(user)
        return Response({"success": f"{user.username} added to conversation"}, status=status.HTTP_200_OK)
    