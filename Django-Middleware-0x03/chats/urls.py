from django.urls import path
from .views import UserMessageList

urlpatterns = [
    path('messages/', UserMessageList.as_view(), name='user_messages'),
]
