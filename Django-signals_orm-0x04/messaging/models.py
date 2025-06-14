from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager


class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(
            receiver=user,
            read=False
        ).only('id', 'sender', 'content', 'timestamp')


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        read = models.BooleanField(default=False) )

    objects = models.Manager()  
    unread = UnreadMessagesManager()  
        
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='edited_messages',
        on_delete=models.SET_NULL
    )
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    # Managers
    objects = models.Manager()  # Default
    unread = UnreadMessagesManager()  # Custom for unread messages

    def __str__(self):
        return f"Msg {self.id} from {self.sender} to {self.receiver}"

    def get_thread(self):
        thread = []

        def fetch_replies(message):
            replies = message.replies.all()
            for reply in replies:
                thread.append(reply)
                fetch_replies(reply)

        fetch_replies(self)
        return thread


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - Msg {self.message.id}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of Msg {self.message.id} edited by {self.edited_by}"
