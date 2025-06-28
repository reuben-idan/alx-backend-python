from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import UserView, ConversationView, MessageView, health_check

router = DefaultRouter()
router.register(r'conversations', ConversationView, basename='conversations')

# nested router for messages.
convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup = 'conversation')
convo_router.register(r'messages', MessageView, basename='conversation-messages')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', include(router.urls)),
    path('', include(convo_router.urls)),
]