import django_filters
from .models import Message  # ✅ Add this line
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['author', 'content', 'timestamp']
