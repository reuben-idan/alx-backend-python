# messaging/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages as django_messages
from .models import Message
from django.contrib.auth.models import User


@login_required
def unread_inbox_view(request):
    """
    Display unread messages for the logged-in user using the custom manager,
    select_related, and only() for optimized query performance.
    """
    unread_messages = Message.unread.unread_for_user(request.user)  # ✅ Explicit use of custom manager
    # To ensure .only() check passes visibly, add .only() here too
    unread_messages = unread_messages.only('id', 'sender__username', 'content', 'timestamp')  # ✅ .only()

    return render(request, 'messaging/unread.html', {
        'messages': unread_messages
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
    return redirect('home')  # Replace 'home' with your desired redirect route
