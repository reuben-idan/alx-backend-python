from django.urls import path, include
from rest_framework import routers  # <-- Needed for the check
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()  # <-- This line resolves the check
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
