from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Delete messages where the user is either sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete related notifications
    Notification.objects.filter(user=instance).delete()

    # Delete any edit histories the user made
    MessageHistory.objects.filter(edited_by=instance).delete()
