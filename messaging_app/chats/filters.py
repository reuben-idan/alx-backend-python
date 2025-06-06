# chats/filters.py

import django_filters
from .models import Message
from django.contrib.auth.models import User

class MessageFilter(django_filters.FilterSet):
    # Filter messages by sender (user) ID or username
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    
    # Filter messages by timestamp range
    start_time = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='gte')
    end_time = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['author', 'start_time', 'end_time']
