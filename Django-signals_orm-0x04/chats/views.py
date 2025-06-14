# chats/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Message
from django.contrib.auth.models import User

# Cache this view for 60 seconds
@cache_page(60)
@login_required
def conversation_view(request, username):
    """
    Display the conversation between the logged-in user and another user.
    The output is cached for 60 seconds to improve performance.
    """
    other_user = get_object_or_404(User, username=username)
    
    # Fetch all messages between the two users (simplified)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'chats/conversation.html', {
        'messages': messages,
        'other_user': other_user
    })
