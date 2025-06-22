from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Model to create/display the user"""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'user_id','username', 'email', 'first_name', 'last_name',
            'bio', 'phone_number', 'password', 'confirm_password'
        ]
        read_only_fields = ['user_id']

    def validate(self, data):
        """Validate password to:
        1. Ensure it is provided during create.
        2. Exclude it as required from PUT and PATCH  if not provided
        """
        if self.context['request'].method == 'POST':
            if not data.get('password') or not data.get('confirm_password'):
                raise serializers.ValidationError("Password and confirm_password are required.")
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError("Passwords do not match")
        
        if len(data.get('phone_number')) > 15:
            raise serializers.ValidationError("Phone number cannot be null or have more than 15 characters.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        # Only update password if both are provided and match
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Passwords do not match."})
            instance.set_password(password)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ConversationSerializer(serializers.ModelSerializer):
    """Create conversation serializer"""
    participants = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all(),
        required = False
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Create Message Serializer"""
    username = serializers.CharField(source='sender.username', read_only=True)
    first_name = serializers.CharField(source='sender.first_name', read_only=True)
    last_name = serializers.CharField(source='sender.last_name', read_only=True)
    message_body = serializers.CharField(max_length = 1000)

    class Meta:
        model = Message
        fields = [
            'message_id', 'username', 'first_name', 'last_name',
            'conversation', 'message_body', 'sent_at'
        ]
        read_only_fields = [
            'message_id', 'sent_at', 'username', 'first_name', 'last_name', 'conversation'
        ]

