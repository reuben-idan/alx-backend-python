from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User,
        related_name='edited_messages',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        help_text="Optional. Indicates this message is a reply to another."
    )

    def __str__(self):
        return f"Msg {self.id} from {self.sender} to {self.receiver}"

    def get_thread(self):
        """
        Recursively fetch all nested replies to this message.
        """
        thread = []

        def fetch_replies(message):
            replies = message.replies.all()
            for reply in replies:
                thread.append(reply)
                fetch_replies(reply)

        fetch_replies(self)
        return thread


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} (Msg ID: {self.message.id})"


class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='history',
        on_delete=models.CASCADE
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"History for Message {self.message.id} at {self.edited_at}"
