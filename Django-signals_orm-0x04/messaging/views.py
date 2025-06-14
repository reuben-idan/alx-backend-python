# messaging/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages
from .models import Message
from django.contrib.auth.models import User


@login_required
def unread_inbox_view(request):
    """
    Display unread messages for the logged-in user.
    Optimized with .only() to load only essential fields.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/unread.html', {
        'messages': unread_messages
    })


@login_required
def threaded_conversation_view(request, message_id):
    """
    Display a message and its threaded replies using select_related and prefetch_related.
    """
    root_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver')
                       .prefetch_related('replies__sender', 'replies__receiver'),
        pk=message_id,
        receiver=request.user
    )
    thread = root_message.get_thread()
    return render(request, 'messaging/thread.html', {
        'root_message': root_message,
        'replies': thread
    })


@require_POST
@login_required
def delete_user_view(request):
    """
    Delete the currently authenticated user.
    Related data is cleaned up via post_delete signal.
    """
    user = request.user
    username = user.username
    user.delete()
    django_messages.success(request, f"Account '{username}' and all related data deleted.")
    return redirect('home')  # or your login/landing page
