from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import UserViewSet, MessageViewSet

# Parent router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# Nested router
nested_router = NestedDefaultRouter(router, r'users', lookup='user')
nested_router.register(r'messages', MessageViewSet, basename='user-messages')

urlpatterns = router.urls + nested_router.urls
