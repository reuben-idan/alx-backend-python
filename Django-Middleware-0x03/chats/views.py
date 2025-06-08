from django.shortcuts import render
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Conversation, Message
from .permissions import IsParticipantOfConversation
from rest_framework.permissions import IsAuthenticated


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations for conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] 
    search_fields = ['participants__username']
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def list(self, request, *args, **kwargs):
        """
        List all conversations with their participants and messages.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expects a list of user IDs in 'participants'.
        """
        participants = request.data.get('participants', [])
        if not participants or not isinstance(participants, list):
            return Response({'error': 'Participants must be a list of user IDs.'}, status=status.HTTP_400_BAD_REQUEST)
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides CRUD operations for messages within conversations.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    def list(self, request, *args, **kwargs):
        """
        List all messages with their sender and conversation details.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Expects 'conversation', 'sender', and 'message_body' in the request data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)