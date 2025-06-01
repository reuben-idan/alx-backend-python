from rest_framework import serializers
from .models import CustomUser, Conversation, Message

# ✅ Serializer for CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number']

# ✅ Serializer for Message
class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)  # Optional: nested user info

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at', 'created_at']

# ✅ Serializer for Conversation with nested messages and participants
class ConversationSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
