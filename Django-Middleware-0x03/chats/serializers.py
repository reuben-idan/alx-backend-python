from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'bio', 'display_name'
        ]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    short_message = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id', 'conversation', 'sender', 'message_body',
            'sent_at', 'short_message'
        ]

    def get_short_message(self, obj):
        # Return the first 20 characters of the message body
        return obj.message_body[:20]

    def validate_message_body(self, value):
   #raise errors if the message body is empty
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']