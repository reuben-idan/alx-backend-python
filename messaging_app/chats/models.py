"""Models for the user, conversation and the messages"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator


class User(AbstractUser):
    """User-defined fields extending Django's AbstractUser."""
    user_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'email']

    def __str__(self):
        return self.username

    @property
    def id(self):
        return self.user_id


class Conversation(models.Model):
    """Model representing conversations between users."""
    conversation_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.conversation_id} with {self.participants.count()} participants"

    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    """Model representing a message in a conversation."""
    message_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    message_body = models.TextField(validators=[MaxLengthValidator(1000)])
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_id} sent by {self.sender.username}"

    class Meta:
        ordering = ['sent_at'] # oldest messages first.



