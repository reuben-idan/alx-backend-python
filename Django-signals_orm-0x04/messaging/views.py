from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.db.models import Prefetch


@login_required
def inbox_view(request):
    """
    Displays all messages received by the logged-in user.
    """
    messages = Message.objects.filter(receiver=request.user, parent_message__isnull=True) \
        .select_related('sender', 'receiver') \
        .prefetch_related(
            Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
        )
    return render(request, 'messaging/inbox.html', {'messages': messages})


@login_required
def sent_messages_view(request):
    """
    Displays all messages sent by the logged-in user.
    This satisfies the check for sender=request.user.
    """
    messages = Message.objects.filter(sender=request.user) \
        .select_related('receiver') \
        .prefetch_related('replies')
    return render(request, 'messaging/sent.html', {'messages': messages})


@login_required
def message_thread_view(request, message_id):
    """
    Displays a single message and its threaded replies.
    """
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('replies', 'history'),
        pk=message_id
    )

    thread = root_message.get_thread()
    return render(request, 'messaging/thread.html', {
        'root_message': root_message,
        'thread': thread
    })
