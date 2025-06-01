from rest_framework import serializers
from .models import CustomUser, Conversation, Message

# ✅ Serializer for CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()  # Explicit CharField usage

    class Meta:
        model = CustomUser
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number']

# ✅ Serializer for Message
class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at', 'created_at']

# ✅ Serializer for Conversation with nested messages using SerializerMethodField
class ConversationSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        if 'participants' in data and not data['participants']:
            raise serializers.ValidationError("Conversation must have at least one participant.")
        return data

