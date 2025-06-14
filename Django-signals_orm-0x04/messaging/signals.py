from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification


@receiver(pre_save, sender=Message)
def log_message_edits(sender, instance, **kwargs):
    """
    Logs the old content of a message before it's edited,
    and creates a history entry in the MessageHistory model.
    """
    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=instance.edited_by  # Capture who made the edit
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass  # Likely a new message, no previous content to track


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Automatically delete all related messages, notifications,
    and message histories when a user account is deleted.
    """
    # Delete messages where the user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications for the user
    Notification.objects.filter(user=instance).delete()

    # Delete message histories where user edited
    MessageHistory.objects.filter(edited_by=instance).delete()
